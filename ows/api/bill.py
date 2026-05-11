from __future__ import annotations
from dataclasses import asdict
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ows.client import OwsClient
from ows.models import BillItem, BillDetail, BillMonthRequest, _from_dict

BILL_TYPE = {
    1: "Instance",
    2: "Traffic",
}


class BillAPI:
    def __init__(self, client: OwsClient):
        self._client = client

    def get_detail_by_month(self, req: BillMonthRequest = None) -> BillDetail:
        if req is None:
            req = BillMonthRequest()
        data = self._client.post("/console/bill/getDetailByMonth", asdict(req))
        items = [_from_dict(BillItem, item) for item in data.get("list", [])]
        return BillDetail(
            list=items,
            invid=data.get("invid", ""),
            user_total_money=data.get("user_total_money", "0"),
            total_gift=data.get("total_gift", "0"),
        )
