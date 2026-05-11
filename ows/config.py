import json
import os
from dataclasses import dataclass


@dataclass
class Config:
    """ows.us API credentials (app_id, app_secret, optional sos_token)."""

    app_id: str
    app_secret: str
    sos_token: str = ""

    @classmethod
    def load(cls, path: str = "config.json") -> "Config":
        """Load config from a JSON file.

        Args:
            path: Path to the JSON config file. Defaults to "config.json".

        Returns:
            A Config instance populated from the file.
        """
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls(
            app_id=data["app_id"],
            app_secret=data["app_secret"],
            sos_token=data.get("sos_token", ""),
        )

    @classmethod
    def from_env(cls) -> "Config":
        """Load config from environment variables.

        Reads ``OWS_APP_ID``, ``OWS_APP_SECRET``, and optionally
        ``OWS_SOS_TOKEN``.

        Raises:
            FileNotFoundError: If either env var is not set.

        Returns:
            A Config instance from environment variables.
        """
        app_id = os.environ.get("OWS_APP_ID", "")
        app_secret = os.environ.get("OWS_APP_SECRET", "")
        if not app_id or not app_secret:
            raise FileNotFoundError(
                "config.json not found and OWS_APP_ID/OWS_APP_SECRET env vars not set"
            )
        return cls(
            app_id=app_id,
            app_secret=app_secret,
            sos_token=os.environ.get("OWS_SOS_TOKEN", ""),
        )
