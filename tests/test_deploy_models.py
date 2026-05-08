"""Tests for deploy-related models."""
import pytest
from ows.models import VpsLoginInfo, DeployRequest, DeployResult


class TestVpsLoginInfo:
    def test_defaults(self):
        info = VpsLoginInfo(vps_id="abc", password="pass", ip="1.2.3.4")
        assert info.os == "ubuntu 20.04"
        assert info.vps_type == "1C-2G"
        assert info.user == "root"
        assert info.port == "22"

    def test_no_defaults(self):
        info = VpsLoginInfo(
            vps_id="x", password="p", ip="1.1.1.1",
            os="debian", vps_type="2C-4G", user="admin", port="2222",
        )
        assert info.os == "debian"
        assert info.vps_type == "2C-4G"
        assert info.user == "admin"
        assert info.port == "2222"


class TestDeployRequest:
    def test_defaults(self):
        req = DeployRequest(
            region_id="Tokyo (Japan)",
            vcpus=1,
            memory=1024,
            disk=15,
            vps_infos=[VpsLoginInfo(vps_id="abc", password="p", ip="1.2.3.4")],
        )
        assert req.vps_brand_id == "ows.us"
        assert req.quota_type == 0
        assert req.quota == 2000
        assert req.bandwidth == 100
        assert req.group_id == "Vip HighSpeed Server"
        assert req.tag == "metro"

    def test_unlimited_quota(self):
        req = DeployRequest(
            region_id="Singapore (Singapore)",
            vcpus=2,
            memory=2048,
            disk=30,
            quota_type=1,
            quota=0,
            vps_infos=[VpsLoginInfo(vps_id="x", password="p", ip="1.1.1.1")],
        )
        assert req.quota_type == 1


class TestDeployResult:
    def test_success(self):
        r = DeployResult(code=200, msg="success", ip="")
        assert r.code == 200

    def test_failure(self):
        r = DeployResult(code=400, msg="error", ip="192.168.1.1")
        assert r.code == 400
        assert r.ip == "192.168.1.1"
