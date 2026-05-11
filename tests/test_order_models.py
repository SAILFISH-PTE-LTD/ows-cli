"""Tests for order and bill models."""
import pytest
from ows.models import Order, OrderListRequest, BillItem, BillDetail, BillMonthRequest, _from_dict


class TestOrder:
    def test_from_dict(self):
        data = {
            "id": 25737, "uid": 11688, "order_sn": "OWS123", "payid": 25737,
            "status": 1, "type": 1, "product_type": 1,
            "product_info": '{"order_price":200}',
            "original_price": 200, "amount": 200, "discount": 0,
            "ctime": "2026-05-08 16:41:52", "utime": "2026-05-08 16:43:50",
            "create_time": 1778229712, "update_time": 1778229830,
            "delete_time": 0, "remark": "", "boss_remark": "",
        }
        o = _from_dict(Order, data)
        assert o.id == 25737
        assert o.order_sn == "OWS123"
        assert o.status == 1
        assert o.amount == 200
        assert o.ctime == "2026-05-08 16:41:52"

    def test_ignores_unknown_fields(self):
        o = _from_dict(Order, {"id": 1, "unknown_field": "should be ignored"})
        assert o.id == 1

    def test_str_price_converted_to_float(self):
        o = _from_dict(Order, {"id": 1, "amount": "200.50", "original_price": "300.00"})
        assert o.amount == 200.50
        assert o.original_price == 300.00


class TestOrderListRequest:
    def test_defaults(self):
        req = OrderListRequest()
        assert req.page_num == 1
        assert req.page_size == 10
        assert req.status == 0
        assert req.product_type == 0
        assert req.begin_date == ""
        assert req.end_date == ""

    def test_custom(self):
        req = OrderListRequest(page_num=2, page_size=5, status=1, time_sort=1)
        assert req.page_num == 2
        assert req.status == 1
        assert req.time_sort == 1


class TestBillItem:
    def test_from_dict(self):
        data = {
            "sid": 1148532, "region_id": 7, "total_money": "2.87423100",
            "start_time": 1777594038, "end_time": 1778238438,
            "total": 180, "quantity": 180, "display_value": "0",
            "max_quantity": 1, "type": 1, "server_end_time": 1778238438,
            "product_info": '{"cores":"1","memory":"2"}',
            "name": "Planet-MNL01-0PQcMs", "product_type": 2,
            "product_name": "ECS", "ip": "195.86.215.10",
            "region_name": "MNL01", "description": "Panets <195.86.215.10> [MNL01]",
        }
        item = _from_dict(BillItem, data)
        assert item.sid == 1148532
        assert item.total_money == "2.87423100"
        assert item.type == 1
        assert item.name == "Planet-MNL01-0PQcMs"
        assert item.ip == "195.86.215.10"
        assert item.region_name == "MNL01"

    def test_traffic_item(self):
        data = {
            "sid": 0, "region_id": 7, "total_money": "61.35",
            "type": 2, "name": "", "ip": "", "product_name": "",
            "description": "Traffic [MNL01]", "region_name": "MNL01",
            "quantity": 1227, "total": 1227, "max_quantity": 33,
        }
        item = _from_dict(BillItem, data)
        assert item.sid == 0
        assert item.type == 2
        assert item.description == "Traffic [MNL01]"


class TestBillDetail:
    def test_from_data(self):
        items = [
            _from_dict(BillItem, {"sid": 1, "total_money": "10.00", "type": 1}),
            _from_dict(BillItem, {"sid": 0, "total_money": "5.00", "type": 2}),
        ]
        detail = BillDetail(
            list=items, invid="INV-001",
            user_total_money="15.00", total_gift="0",
        )
        assert len(detail.list) == 2
        assert detail.invid == "INV-001"
        assert detail.user_total_money == "15.00"


class TestBillMonthRequest:
    def test_defaults(self):
        req = BillMonthRequest()
        assert req.begin_date == ""
        assert req.end_date == ""
        assert req.team_uuid == ""

    def test_custom(self):
        req = BillMonthRequest(begin_date="1775001600", end_date="1777593599", team_uuid="xyz")
        assert req.begin_date == "1775001600"
        assert req.team_uuid == "xyz"
