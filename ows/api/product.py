from __future__ import annotations
from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from ows.client import OwsClient
from ows.models import StatusResult, _from_dict
from dataclasses import dataclass, field


@dataclass
class Region:
    """Represents a geographic region with zone and city information.

    Attributes:
        id: Region identifier.
        name: Region display name.
        children: Child regions.
        country: Country name.
        coordinate: Geographic coordinates.
        flag_code: Country flag code.
        zone: Availability zones.
        region_id: Region ID.
        status: Region status.
        city_code: City code.
    """
    id: int = 0
    name: str = ""
    children: list = field(default_factory=list)
    country: str = ""
    coordinate: str = ""
    flag_code: str = ""
    zone: list = field(default_factory=list)
    region_id: int = 0
    status: int = 0
    city_code: str = ""


class ProductAPI:
    """API client for general product operations.

    Provides methods for resource lifecycle operations including
    destruction, status queries, and region lookup.
    """
    def __init__(self, client: OwsClient):
        self._client = client

    def free(self, uuid: str) -> None:
        """Permanently destroy (free) a resource.

        Args:
            uuid: Resource UUID to destroy.
        """
        self._client.post("/console/product/freed", {"uuid": uuid})

    def get_status(self, uuid: str) -> StatusResult:
        """Check resource status by UUID.

        Args:
            uuid: Resource UUID.

        Returns:
            StatusResult: Result with numeric status code.
        """
        data = self._client.post("/console/product/getStatusByUuid", {"uuid": uuid})
        return _from_dict(StatusResult, data)

    def get_region(self, category_uuid: str = "") -> List[Region]:
        """List available regions with zone/city information.

        Args:
            category_uuid: Optional category UUID filter. Empty string returns all regions.

        Returns:
            List[Region]: Available regions.
        """
        data = self._client.post("/console/product/getRegion", {"category_uuid": category_uuid})
        return [_from_dict(Region, item) for item in (data or [])]
