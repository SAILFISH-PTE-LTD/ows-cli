import requests
from ows.auth import AuthSession
from ows.config import Config
from ows.errors import APIError, AuthError, NetworkError
from ows.api.planet import PlanetAPI
from ows.api.product import ProductAPI
from ows.api.order import OrderAPI
from ows.deploy import DeployClient


class OwsClient:
    BASE_URL = "https://api.ows.us"

    def __init__(self, auth: AuthSession, timeout: int = 30, max_retries: int = 1,
                 sos_token: str = None):
        self.auth = auth
        self.timeout = timeout
        self.max_retries = max_retries
        self.planet = PlanetAPI(self)
        self.product = ProductAPI(self)
        self.order = OrderAPI(self)
        self.deploy = DeployClient(sos_token) if sos_token else None

    @classmethod
    def from_config(cls, path: str = "config.json", **kwargs) -> "OwsClient":
        config = Config.load(path)
        auth = AuthSession(config)
        sos_token = kwargs.pop("sos_token", config.sos_token) or None
        return cls(auth, sos_token=sos_token, **kwargs)

    def post(self, path: str, data: dict = None) -> dict:
        return self._request("POST", path, json=data or None, params=None)

    def post_query(self, path: str, params: dict = None) -> dict:
        return self._request("POST", path, json=None, params=params or None)

    def get(self, path: str, params: dict = None) -> dict:
        return self._request("GET", path, json=None, params=params or None)

    def _request(self, method: str, path: str, json: dict, params: dict) -> dict:
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
        body = resp.json()
        code = body.get("code")
        if code == 110:
            raise AuthError(f"token invalid or expired: {body.get('message', '')}")
        if code != 200:
            raise APIError(code, body.get("message", ""), body.get("data"))
        return body.get("data", {})
