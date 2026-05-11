from __future__ import annotations
from dataclasses import asdict
from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from ows.client import OwsClient
from ows.models import (
    PlanetType, Image, Flavor, PriceRequest, PriceResult,
    CreateRequest, CreateResult, ListRequest, Instance, InstanceDetail,
    ListResult, _from_dict,
)


class PlanetAPI:
    def __init__(self, client: OwsClient):
        self._client = client

    # --- Info ---

    def get_planet_type(self) -> List[PlanetType]:
        data = self._client.post("/console/planet/getPlanetType")
        return [_from_dict(PlanetType, item) for item in (data or [])]

    def get_image_by_region(self, region_uuid: str, is_self: int = 0) -> List[Image]:
        data = self._client.post("/console/planet/getImageByRegion", {
            "region_uuid": region_uuid, "is_self": is_self
        })
        return [_from_dict(Image, item) for item in (data or [])]

    def get_flavor_by_add(self, region_uuid: str, category_uuid: str) -> List[Flavor]:
        data = self._client.post("/console/planet/getFlavorByAdd", {
            "region_uuid": region_uuid, "category_uuid": category_uuid
        })
        return [_from_dict(Flavor, item) for item in (data or [])]

    # --- Price & Create ---

    def get_price(self, req: PriceRequest) -> PriceResult:
        data = self._client.post("/console/planet/getPrice", asdict(req))
        return _from_dict(PriceResult, data)

    def create(self, req: CreateRequest) -> CreateResult:
        data = self._client.post("/console/planet/add", asdict(req))
        if isinstance(data, list):
            data = {}
        return _from_dict(CreateResult, data) if data else CreateResult(uuid="")

    # --- Instance lifecycle ---

    def list_instances(self, req: ListRequest = None) -> ListResult[Instance]:
        if req is None:
            req = ListRequest()
        data = self._client.post("/console/planet/list", asdict(req))
        instances = [_from_dict(Instance, item) for item in data.get("list", [])]
        return ListResult(list=instances, total=data.get("total", 0))

    def get_detail(self, uuid: str, project_uuid: str = None) -> InstanceDetail:
        body = {"uuid": uuid}
        if project_uuid:
            body["project_uuid"] = project_uuid
        data = self._client.post("/console/planet/getDetail", body)
        return _from_dict(InstanceDetail, data)

    def stop(self, uuid: str) -> None:
        self._client.post("/console/planet/stop", {"uuid": uuid})

    def start(self, uuid: str) -> None:
        self._client.post("/console/planet/start", {"uuid": uuid})

    def reboot(self, uuid: str, reboot_type: int) -> None:
        self._client.post("/console/planet/reboot", {"uuid": uuid, "reboot_type": reboot_type})
