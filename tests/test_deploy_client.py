"""Tests for DeployClient."""
import json
import base64
import urllib.parse
import pytest
from unittest.mock import patch, MagicMock
from ows.deploy import DeployClient, REGION_MAP
from ows.models import DeployRequest, DeployResult, VpsLoginInfo


class TestRegionMap:
    def test_known_city(self):
        assert REGION_MAP["Tokyo"] == "Tokyo (Japan)"
        assert REGION_MAP["Amsterdam"] == "Amsterdam (Netherlands)"
        assert REGION_MAP["Singapore"] == "Singapore (Singapore)"

    def test_missing_city_raises(self):
        with pytest.raises(KeyError):
            REGION_MAP["Mars"]


class TestDeployClient:
    def _make_client(self):
        return DeployClient(sos_token="test-token")

    def _make_req(self):
        return DeployRequest(
            region_id="Tokyo (Japan)",
            vcpus=1,
            memory=1024,
            disk=15,
            vps_infos=[VpsLoginInfo(vps_id="abc", password="pass", ip="1.2.3.4")],
        )

    def test_init_without_token(self):
        with pytest.raises(ValueError, match="sos_token"):
            DeployClient(sos_token="")

    def test_build_headers(self):
        client = self._make_client()
        headers = client._build_headers()
        assert headers["Content-Type"] == "application/x-www-form-urlencoded;charset=UTF-8"
        assert headers["se-ua"] == "web"
        assert headers["channel"] == "MetroVPN"
        assert headers["operation"] == "unknown"
        assert headers["token"] == "test-token"
        assert "ts" in headers

    def test_encode_body(self):
        client = self._make_client()
        req = self._make_req()
        body = client._encode_body(req)
        assert body.startswith("form_data=")
        encoded = body[len("form_data="):]
        decoded = base64.b64decode(urllib.parse.unquote(encoded))
        inner = json.loads(decoded)
        assert inner["vps_brand_id"] == "ows.us"
        assert inner["tag"] == "metro"
        assert len(inner["vps_infos"]) == 1

    @patch("ows.deploy.requests.post")
    def test_create_deploy_success(self, mock_post):
        client = self._make_client()
        req = self._make_req()
        inner = {"code": 200, "data": {"msg": "success", "ip": ""}}
        encoded = base64.b64encode(json.dumps(inner).encode()).decode()
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"code": 200, "data": encoded}
        mock_post.return_value = mock_resp

        result = client.create_deploy(req)
        assert result.code == 200
        assert result.msg == "success"

    @patch("ows.deploy.requests.post")
    def test_create_deploy_failure(self, mock_post):
        client = self._make_client()
        req = self._make_req()
        inner = {"code": 400, "data": {"msg": "bad request", "ip": "1.2.3.4"}}
        encoded = base64.b64encode(json.dumps(inner).encode()).decode()
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"code": 200, "data": encoded}
        mock_post.return_value = mock_resp

        result = client.create_deploy(req)
        assert result.code == 400
        assert result.msg == "bad request"
        assert result.ip == "1.2.3.4"

    @patch("ows.deploy.requests.post")
    def test_create_deploy_retry_on_rate_limit(self, mock_post):
        client = self._make_client()
        req = self._make_req()
        msg_text = "Too many requests, try again after 1 seconds"
        inner1 = {"code": 400, "data": {"msg": msg_text, "ip": ""}}
        encoded1 = base64.b64encode(json.dumps(inner1).encode()).decode()
        resp1 = MagicMock()
        resp1.json.return_value = {"code": 200, "data": encoded1}
        inner2 = {"code": 200, "data": {"msg": "ok", "ip": ""}}
        encoded2 = base64.b64encode(json.dumps(inner2).encode()).decode()
        resp2 = MagicMock()
        resp2.json.return_value = {"code": 200, "data": encoded2}
        mock_post.side_effect = [resp1, resp2]

        result = client.create_deploy(req)
        assert result.code == 200
        assert mock_post.call_count == 2
