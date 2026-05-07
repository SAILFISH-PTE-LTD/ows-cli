import json
from dataclasses import dataclass


@dataclass
class Config:
    app_id: str
    app_secret: str

    @classmethod
    def load(cls, path: str = "config.json") -> "Config":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls(app_id=data["app_id"], app_secret=data["app_secret"])
