"""DeployClient for MetroVPN deployment API (console.metrovpn.xyz)."""
from __future__ import annotations
import json
import base64
import urllib.parse
import time
from dataclasses import asdict

import requests

from ows.models import DeployRequest, DeployResult


# city_name (ows.us) → region_id (deploy system)
REGION_MAP = {
    "Amsterdam": "Amsterdam (Netherlands)",
    "Andhra Pradesh": "Andhra Pradesh (India)",
    "Ashburn": "Ashburn (United States)",
    "Atlanta": "Atlanta (United States)",
    "Bahrain": "Bahrain (Bahrain)",
    "Bangalore": "Bangalore (India)",
    "Bangkok": "Bangkok (Thailand)",
    "Bogota": "Bogota (Colombia)",
    "Boston": "Boston (United States)",
    "Brussels": "Brussels (Belgium)",
    "Bucharest": "Bucharest (Romania)",
    "Buenos Aires": "Buenos Aires (Argentina)",
    "Cairo": "Cairo (Egypt)",
    "Chicago": "Chicago (United States)",
    "Dallas": "Dallas (United States)",
    "Denver": "Denver (United States)",
    "Dhaka": "Dhaka (Bangladesh)",
    "Dubai": "Dubai (United Arab Emirates)",
    "Dublin": "Dublin (Ireland)",
    "Frankfurt": "Frankfurt (Germany)",
    "Fremont": "Fremont (United States)",
    "Hanoi": "Hanoi (Vietnam)",
    "Hillsboro": "Hillsboro (United States)",
    "Hong Kong": "Hong Kong (Hong Kong(China))",
    "Ireland": "Ireland (Ireland)",
    "Istanbul": "Istanbul (Turkey)",
    "Jakarta": "Jakarta (Indonesia)",
    "Johannesburg": "Johannesburg (South Africa)",
    "Kiev": "Kiev (Ukraine)",
    "Kuala Lumpur": "Kuala Lumpur (Malaysia)",
    "Lagos": "Lagos (Nigeria)",
    "Lima": "Lima (Peru)",
    "London": "London (United Kingdom)",
    "Los Angeles": "Los Angeles (United States)",
    "Madrid": "Madrid (Spain)",
    "Manila": "Manila (Philippines)",
    "Mexico City": "Mexico City (Mexico)",
    "Miami": "Miami (United States)",
    "Milan": "Milan (Italy)",
    "Montreal": "Montreal (Canada)",
    "Moscow": "Moscow (Russia)",
    "Mumbai": "Mumbai (India)",
    "Nairobi": "Nairobi (Kenya)",
    "New York": "New York (United States)",
    "Newark": "Newark (United States)",
    "Ohio": "Ohio (United States)",
    "Oregon": "Oregon (United States)",
    "Paris": "Paris (France)",
    "Phnom Penh": "Phnom Penh (Cambodia)",
    "Riyadh": "Riyadh (Saudi Arabia)",
    "San Francisco": "San Francisco (United States)",
    "Santa Clara": "Santa Clara (United States)",
    "Sao Paulo": "Sao Paulo (Brazil)",
    "Seattle": "Seattle (United States)",
    "Seoul": "Seoul (South Korea)",
    "Silicon Valley": "Silicon Valley (United States)",
    "Singapore": "Singapore (Singapore)",
    "Strasbourg": "Strasbourg (France)",
    "Sydney": "Sydney (Australia)",
    "Taipei": "Taipei (ROC(TW))",
    "TaiPei": "Taipei (ROC(TW))",
    "Tel Aviv": "Tel Aviv (Israel)",
    "Tokyo": "Tokyo (Japan)",
    "Toronto": "Toronto (Canada)",
    "Vancouver": "Vancouver (Canada)",
    "Vienna": "Vienna (Austria)",
    "Vint Hill": "Vint Hill (United States)",
    "Virginia": "Virginia (United States)",
    "Warsaw": "Warsaw (Poland)",
    "Yangon": "Yangon (Myanmar)",
}


class DeployClient:
    BASE_URL = "https://console.metrovpn.xyz"

    def __init__(self, sos_token: str, timeout: int = 30):
        if not sos_token or not sos_token.strip():
            raise ValueError("sos_token is required for DeployClient")
        self.sos_token = sos_token.strip()
        self.timeout = timeout

    def create_deploy(self, req: DeployRequest) -> DeployResult:
        body = self._encode_body(req)
        headers = self._build_headers()
        max_retries = 1
        for attempt in range(max_retries + 1):
            try:
                resp = requests.post(
                    f"{self.BASE_URL}/vps/create-deploy",
                    data=body,
                    headers=headers,
                    timeout=(10, self.timeout),
                )
                result = self._parse_response(resp)
                if result.code == 200:
                    return result
                msg_lower = result.msg.lower()
                if attempt < max_retries and (
                    "too many requests" in msg_lower or "too frequent" in msg_lower
                ):
                    time.sleep(2)
                    continue
                return result
            except requests.exceptions.RequestException:
                if attempt < max_retries:
                    time.sleep(2)
                    continue
                raise

    def _build_headers(self) -> dict:
        return {
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
            "se-ua": "web",
            "ts": str(int(time.time() * 1000)),
            "channel": "MetroVPN",
            "operation": "unknown",
            "token": self.sos_token,
        }

    def _encode_body(self, req: DeployRequest) -> str:
        encoded = base64.b64encode(json.dumps(asdict(req)).encode()).decode()
        return f"form_data={urllib.parse.quote(encoded, safe='')}"

    def _parse_response(self, resp) -> DeployResult:
        inner = json.loads(base64.b64decode(resp.text))
        inner_data = inner.get("data", {})
        if not isinstance(inner_data, dict):
            inner_data = {}
        return DeployResult(
            code=inner.get("code", 0),
            msg=inner.get("msg") or inner_data.get("msg", ""),
            ip=inner_data.get("ip", ""),
        )
