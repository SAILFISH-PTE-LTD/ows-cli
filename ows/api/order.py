from __future__ import annotations
from dataclasses import asdict
from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from ows.client import OwsClient
from ows.models import Order, OrderListRequest, ListResult, _from_dict


# Mapping of order status codes to human-readable labels.
ORDER_STATUS = {
    0: "Not Paid",
    1: "Paid",
    2: "Expired",
    3: "Deleted",
}


class OrderAPI:
    """API client for billing order operations.

    Provides methods for listing and querying billing orders.
    """
    def __init__(self, client: OwsClient):
        self._client = client

    def list_orders(self, req: OrderListRequest = None) -> ListResult[Order]:
        """List billing orders / charge records.

        Args:
            req: Optional filter/pagination request. Defaults to empty OrderListRequest.

        Returns:
            ListResult[Order]: Paginated list of orders.
        """
        if req is None:
            req = OrderListRequest()
        data = self._client.post("/console/order/list", asdict(req))
        orders = [_from_dict(Order, item) for item in data.get("list", [])]
        return ListResult(list=orders, total=data.get("total", 0))
