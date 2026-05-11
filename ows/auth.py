import time
import requests
from ows.config import Config
from ows.errors import AuthError


class AuthSession:
    """Manages ows.us API authentication lifecycle.

    Handles token acquisition, refresh, and expiry.
    """

    BASE_URL = "https://api.ows.us"

    def __init__(self, config: Config):
        self.config = config
        self.access_token = None
        self.refresh_token = None
        self.expires_at = 0.0

    def get_token(self) -> str:
        """Get a valid access token, refreshing or re-authenticating if needed.

        Returns:
            A valid access token string.
        """
        self._ensure_token()
        return self.access_token

    def _ensure_token(self):
        """Check token validity, refresh or re-auth as needed.

        If no token exists, acquires a new one. If token is expired,
        attempts refresh first, then falls back to re-authentication.
        If token expires within 5 minutes, proactively refreshes.
        """
        now = time.time()
        if not self.access_token:
            self._get_token()
        elif self.expires_at <= now:
            try:
                self._refresh_token()
            except AuthError:
                self._get_token()
        elif self.expires_at - now < 300:
            try:
                self._refresh_token()
            except AuthError:
                pass

    def _get_token(self):
        """Obtain new token pair via POST /console/auth/getToken.

        Raises:
            AuthError: If the authentication request fails.
        """
        resp = requests.post(
            f"{self.BASE_URL}/console/auth/getToken",
            params={"appid": self.config.app_id, "app_secret": self.config.app_secret},
            timeout=(10, 30),
        )
        data = self._parse_response(resp)
        self.access_token = data["access_token"]
        self.refresh_token = data["refresh_token"]
        self.expires_at = time.time() + data.get("expires_in", 7200)

    def _refresh_token(self):
        """Refresh access token via POST /console/auth/refreshToken.

        Raises:
            AuthError: If the refresh request fails.
        """
        resp = requests.post(
            f"{self.BASE_URL}/console/auth/refreshToken",
            params={"refresh_token": self.refresh_token},
            timeout=(10, 30),
        )
        data = self._parse_response(resp)
        self.access_token = data["access_token"]
        self.refresh_token = data["refresh_token"]
        self.expires_at = time.time() + data.get("expires_in", 7200)

    def _parse_response(self, resp):
        """Parse auth API response body.

        Args:
            resp: requests.Response object.

        Returns:
            The "data" field from the JSON response body.

        Raises:
            AuthError: When response code is not 200.
        """
        body = resp.json()
        code = body.get("code")
        if code != 200:
            raise AuthError(f"auth failed: code={code} message={body.get('message', '')}")
        return body.get("data", {})
