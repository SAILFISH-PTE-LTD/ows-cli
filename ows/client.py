import os
import requests
from ows.auth import AuthSession
from ows.config import Config
from ows.errors import APIError, AuthError, NetworkError
from ows.api.planet import PlanetAPI
from ows.api.product import ProductAPI
from ows.api.order import OrderAPI
from ows.api.bill import BillAPI

# DeployClient is private — conditionally loaded from ows_deploy/
try:
    from ows_deploy import DeployClient
except ImportError:
    DeployClient = None


class OwsClient:
    """HTTP client for ows.us API. Manages authentication and exposes Planet,
    Product, Order, and Bill API namespaces."""

    BASE_URL = "https://api.ows.us"

    def __init__(self, auth: AuthSession, timeout: int = 30, max_retries: int = 1,
                 sos_token: str = None):
        self.auth = auth
        self.timeout = timeout
        self.max_retries = max_retries
        self.planet = PlanetAPI(self)
        self.product = ProductAPI(self)
        self.order = OrderAPI(self)
        self.bill = BillAPI(self)
        self.deploy = DeployClient(sos_token) if DeployClient and sos_token else None

    @classmethod
    def from_config(cls, path: str = "config.json", **kwargs) -> "OwsClient":
        """Create client from config file (config.json) or environment variables.

        Falls back to OWS_APP_ID / OWS_APP_SECRET env vars if file not found.

        Args:
            path: Path to the JSON config file. Defaults to "config.json".
            **kwargs: Additional keyword arguments passed to the constructor.

        Returns:
            A configured OwsClient instance.
        """
        if os.path.isfile(path):
            config = Config.load(path)
        else:
            config = Config.from_env()
        auth = AuthSession(config)
        sos_token = kwargs.pop("sos_token", config.sos_token) or None
        return cls(auth, sos_token=sos_token, **kwargs)

    def post(self, path: str, data: dict = None) -> dict:
        """Send POST request with JSON body.

        Args:
            path: API endpoint path (e.g. "/console/planet/list").
            data: JSON-serializable request body dict.

        Returns:
            Response data dict from the API.
        """
        return self._request("POST", path, json=data or None, params=None)

    def post_query(self, path: str, params: dict = None) -> dict:
        """Send POST request with query parameters (used for auth).

        Args:
            path: API endpoint path.
            params: Query parameters dict.

        Returns:
            Response data dict from the API.
        """
        return self._request("POST", path, json=None, params=params or None)

    def get(self, path: str, params: dict = None) -> dict:
        """Send GET request with optional query parameters.

        Args:
            path: API endpoint path.
            params: Optional query parameters dict.

        Returns:
            Response data dict from the API.
        """
        return self._request("GET", path, json=None, params=params or None)

    def _request(self, method: str, path: str, json: dict, params: dict) -> dict:
        """Low-level HTTP request with auth header injection and retry.

        Args:
            method: HTTP method ("GET", "POST", etc.).
            path: API endpoint path.
            json: JSON body dict (or None).
            params: Query parameters dict (or None).

        Returns:
            Parsed response data dict.

        Raises:
            NetworkError: When all retry attempts are exhausted.
        """
        url = f"{self.BASE_URL}{path}"
        headers = {"Authorization": f"Bearer {self.auth.get_token()}"}
        attempt = 0
        while True:
            try:
                resp = requests.request(
                    method, url, json=json, params=params,
                    headers=headers,
                    timeout=(10, self.timeout),
                )
                return self._parse(resp)
            except requests.exceptions.RequestException as e:
                attempt += 1
                if attempt > self.max_retries:
                    raise NetworkError(str(e))

    def _parse(self, resp):
        """Parse API response, handling auth errors (code=110) and generic errors.

        Args:
            resp: requests.Response object.

        Returns:
            The "data" field from the JSON response body.

        Raises:
            AuthError: When response code is 110 (token invalid/expired).
            APIError: When response code is not 200.
        """
        body = resp.json()
        code = body.get("code")
        if code == 110:
            raise AuthError(f"token invalid or expired: {body.get('message', '')}")
        if code != 200:
            raise APIError(code, body.get("message", ""), body.get("data"))
        return body.get("data", {})
