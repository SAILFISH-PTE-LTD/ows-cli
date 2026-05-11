# BillController - getDetailByMonth

## API 地址

```
POST https://api.ows.us/console/bill/getDetailByMonth
```

## 返回数据示例

```json
{
    "code": 200,
    "data": {
        "list": [
            {
                "sid": 1148532,
                "region_id": 7,
                "total_money": "2.87423100",
                "start_time": 1777594038,
                "end_time": 1778238438,
                "total": 180,
                "quantity": 180,
                "display_value": "0",
                "max_quantity": 1,
                "type": 1,
                "server_end_time": 1778238438,
                "product_info": "{\"product_type\":2,\"cores\":\"1\",\"memory\":\"2\",\"disk_size\":40,\"disk_type\":1}",
                "name": "Planet-MNL01-0PQcMs",
                "product_type": 2,
                "product_name": "ECS",
                "ip": "195.86.215.10",
                "region_name": "MNL01",
                "description": "Panets  <195.86.215.10> [MNL01]"
            },
            {
                "sid": 1146300,
                "region_id": 24,
                "total_money": "3.44289160",
                "start_time": 1777594121,
                "end_time": 1778425721,
                "total": 232,
                "quantity": 232,
                "display_value": "0",
                "max_quantity": 1,
                "type": 1,
                "server_end_time": 1778425721,
                "product_info": "{\"product_type\":2,\"cores\":\"1\",\"memory\":\"2\",\"disk_size\":40,\"disk_type\":1}",
                "name": "Planet-TPE01-zub85A",
                "product_type": 2,
                "product_name": "ECS",
                "ip": "212.11.60.195",
                "region_name": "TPE01",
                "description": "Panets  <212.11.60.195> [TPE01]"
            },
            {
                "sid": 0,
                "region_id": 7,
                "total_money": "61.35000000",
                "start_time": 1777615200,
                "end_time": 1778428800,
                "total": 1227,
                "quantity": 1227,
                "display_value": "0",
                "max_quantity": 33,
                "type": 2,
                "server_end_time": 1778428800,
                "product_info": "",
                "name": "",
                "product_type": 0,
                "product_name": "",
                "ip": "",
                "region_name": "MNL01",
                "description": "Traffic [MNL01]"
            }
        ],
        "invid": "INVB4lnp2026-05",
        "user_total_money": "181.84167746",
        "total_gift": "0"
    },
    "message": "success"
}
```

## 请求参数（JSON Body）

```json
{
    "begin_date": "1775001600",
    "end_date": "1777593599",
    "team_uuid": "c132d3bf-abdc-1145-4e95-da2d7184fa4f"
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `begin_date` | string | 账单周期起始 Unix 时间戳，秒，UTC+0 |
| `end_date` | string | 账单周期结束 Unix 时间戳，秒，UTC+0 |
| `team_uuid` | string | 团队 UUID |
