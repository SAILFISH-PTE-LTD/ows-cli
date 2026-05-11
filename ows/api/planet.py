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
    """API client for Planet (VPS) management operations.

    Provides methods for instance lifecycle management including
    creation, listing, detail retrieval, and power operations.
    """
    def __init__(self, client: OwsClient):
        self._client = client

    # --- Info ---

    def get_planet_type(self) -> List[PlanetType]:
        """List product categories (Shared vCPU, Dedicated vCPU, Bare Metal).

        Returns:
            List[PlanetType]: Available product categories.
        """
        data = self._client.post("/console/planet/getPlanetType")
        return [_from_dict(PlanetType, item) for item in (data or [])]

    def get_image_by_region(self, region_uuid: str, is_self: int = 0) -> List[Image]:
        """List available OS images in a region.

        Args:
            region_uuid: Region UUID to query images for.
            is_self: Filter for self-owned images (0=all, 1=self only).

        Returns:
            List[Image]: Available OS images.
        """
        data = self._client.post("/console/planet/getImageByRegion", {
            "region_uuid": region_uuid, "is_self": is_self
        })
        return [_from_dict(Image, item) for item in (data or [])]

    def get_flavor_by_add(self, region_uuid: str, category_uuid: str) -> List[Flavor]:
        """List available instance flavors in a region/category.

        Args:
            region_uuid: Region UUID.
            category_uuid: Product category UUID.

        Returns:
            List[Flavor]: Available instance flavors.
        """
        data = self._client.post("/console/planet/getFlavorByAdd", {
            "region_uuid": region_uuid, "category_uuid": category_uuid
        })
        return [_from_dict(Flavor, item) for item in (data or [])]

    # --- Price & Create ---

    def get_price(self, req: PriceRequest) -> PriceResult:
        """Calculate configuration price.

        Args:
            req: Price calculation request with region, flavor, and billing parameters.

        Returns:
            PriceResult: Calculated price details.
        """
        data = self._client.post("/console/planet/getPrice", asdict(req))
        return _from_dict(PriceResult, data)

    def create(self, req: CreateRequest) -> CreateResult:
        """Create a new Planet (VPS) instance.

        Creation is asynchronous; the returned uuid may be empty.
        Use list_instances to retrieve the actual UUID after creation.

        Args:
            req: Creation request with region, image, flavor, and password.

        Returns:
            CreateResult: Result with uuid (may be empty — creation is async).
        """
        data = self._client.post("/console/planet/add", asdict(req))
        if isinstance(data, list):
            data = {}
        return _from_dict(CreateResult, data) if data else CreateResult(uuid="")

    # --- Instance lifecycle ---

    def list_instances(self, req: ListRequest = None) -> ListResult[Instance]:
        """List Planet instances with optional filters.

        Args:
            req: Optional filter/pagination request. Defaults to empty ListRequest.

        Returns:
            ListResult[Instance]: Paginated list of instances.
        """
        if req is None:
            req = ListRequest()
        data = self._client.post("/console/planet/list", asdict(req))
        instances = [_from_dict(Instance, item) for item in data.get("list", [])]
        return ListResult(list=instances, total=data.get("total", 0))

    def get_detail(self, uuid: str, project_uuid: str = None) -> InstanceDetail:
        """Get full instance detail by UUID.

        Args:
            uuid: Instance UUID.
            project_uuid: Optional project UUID filter.

        Returns:
            InstanceDetail: Full instance detail including network and disk information.
        """
        body = {"uuid": uuid}
        if project_uuid:
            body["project_uuid"] = project_uuid
        data = self._client.post("/console/planet/getDetail", body)
        return _from_dict(InstanceDetail, data)

    def stop(self, uuid: str) -> None:
        """Stop a running instance.

        Args:
            uuid: Instance UUID.
        """
        self._client.post("/console/planet/stop", {"uuid": uuid})

    def start(self, uuid: str) -> None:
        """Start a stopped instance.

        Args:
            uuid: Instance UUID.
        """
        self._client.post("/console/planet/start", {"uuid": uuid})

    def reboot(self, uuid: str, reboot_type: int) -> None:
        """Reboot an instance.

        Args:
            uuid: Instance UUID.
            reboot_type: Reboot type (0=soft reboot, 1=hard reboot).
        """
        self._client.post("/console/planet/reboot", {"uuid": uuid, "reboot_type": reboot_type})
