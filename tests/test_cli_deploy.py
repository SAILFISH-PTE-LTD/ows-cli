"""Tests for CLI deploy helpers."""
import pytest
from ows.deploy import REGION_MAP
from ows.models import VpsLoginInfo


class TestResolveRegionId:
    def test_valid_city(self):
        from ows.cli.planet import _resolve_region_id
        assert _resolve_region_id("Tokyo") == "Tokyo (Japan)"

    def test_empty_city_aborts(self):
        from ows.cli.planet import _resolve_region_id
        import click
        with pytest.raises(click.Abort):
            _resolve_region_id("")

    def test_unknown_city_aborts(self):
        from ows.cli.planet import _resolve_region_id
        import click
        with pytest.raises(click.Abort):
            _resolve_region_id("Atlantis")
