from __future__ import annotations
from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from ows.client import OwsClient
from ows.models import StatusResult, _from_dict
from dataclasses import dataclass, field


@dataclass
class Region:
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
    def __init__(self, client: OwsClient):
        self._client = client

    def free(self, uuid: str) -> None:
        self._client.post("/console/product/freed", {"uuid": uuid})

    def get_status(self, uuid: str) -> StatusResult:
        data = self._client.post("/console/product/getStatusByUuid", {"uuid": uuid})
        return _from_dict(StatusResult, data)

    def get_region(self, category_uuid: str = "") -> List[Region]:
        data = self._client.post("/console/product/getRegion", {"category_uuid": category_uuid})
        return [_from_dict(Region, item) for item in (data or [])]
