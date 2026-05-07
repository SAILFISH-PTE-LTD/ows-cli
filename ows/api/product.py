from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ows.client import OwsClient
from ows.models import StatusResult


class ProductAPI:
    def __init__(self, client: OwsClient):
        self._client = client

    def free(self, uuid: str) -> None:
        self._client.post("/console/product/freed", {"uuid": uuid})

    def get_status(self, uuid: str) -> StatusResult:
        data = self._client.post("/console/product/getStatusByUuid", {"uuid": uuid})
        return StatusResult(status=data.get("status", 0))
