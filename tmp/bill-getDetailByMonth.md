# BillController - getDetailByMonth

## 文档地址

```
https://api.ows.us/apidoc/index.html#/api?appKey=console&key=app%255Cconsole%255Ccontroller%255CBillController%2540getDetailByMonth&title=Get%2520Detail%2520By%2520Month
```

## API 地址

```
POST https://api.ows.us/console/bill/getDetailByMonth
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

## 响应字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `list[].sid` | int | 实例 ID，0 表示非实例计费项（如流量） |
| `list[].region_id` | int | 区域 ID |
| `list[].region_name` | string | 区域名称 |
| `list[].total_money` | string | 该项总费用（USD） |
| `list[].start_time` | int | 计费开始时间戳（秒） |
| `list[].end_time` | int | 计费结束时间戳（秒） |
| `list[].total` | int | 计费总时长（10 分钟为一个单位） |
| `list[].quantity` | int | 计费数量 |
| `list[].display_value` | string | 展示值 |
| `list[].max_quantity` | int | 最大并发数（实例为 1，流量按规格） |
| `list[].type` | int | 类型：1=实例，2=流量 |
| `list[].server_end_time` | int | 服务实际结束时间戳（秒） |
| `list[].product_info` | string | 产品配置 JSON 字符串 |
| `list[].name` | string | 实例名称 |
| `list[].product_type` | int | 产品类型 |
| `list[].product_name` | string | 产品类型名称 |
| `list[].ip` | string | 实例 IP |
| `list[].description` | string | 描述信息 |
| `invid` | string | 账单编号 |
| `user_total_money` | string | 用户总费用（USD） |
| `total_gift` | string | 赠送总费用 |
