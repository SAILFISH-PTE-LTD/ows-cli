# 订单接口（OrderController）

> 全局 Header: `Authorization: Bearer {access_token}`
> 统一响应: `code=200` 正常

---

## POST /console/order/list — 订单列表（Get Paid Order List）

> ⚠️ 官方文档标注为 Query 参数，实际 API 使用 JSON Body。

**Body:**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page_num | int | 是 | 页码 |
| page_size | int | 是 | 每页条数 |
| status | int | 否 | 0-Not Paid 1-Paid 2-Expired 3-Deleted |
| product_type | int | 否 | 产品类型 |
| begin_date | string | 否 | 开始日期 |
| end_date | string | 否 | 结束日期 |
| time_sort | int | 否 | 时间排序 |
| price_sort | int | 否 | 价格排序 |

**响应 data.list[]（实际返回 vs 文档):**

| 字段 | 类型 | 说明 | 来源 |
|------|------|------|------|
| id | int | 订单 ID | 文档+实际 |
| uid | int | 用户 ID | 文档+实际 |
| order_sn | string | 订单号 | 文档+实际 |
| payid | int | 支付 ID | 实际 |
| status | int | 0-Not Paid 1-Paid 2-Expired 3-Deleted | 文档+实际 |
| type | int | 1-New 2-Renew 3-Upgrade | 文档+实际 |
| product_type | int | 产品类型 | 实际 |
| product_info | string | 产品信息 JSON | 实际 |
| original_price | float | 原价 | 实际 |
| amount | float | 实付金额 | 文档+实际 |
| discount | float | 折扣 | 实际 |
| ctime | string | 创建时间 | 文档+实际 |
| utime | string | 更新时间 | 文档+实际 |
| create_time | int/string | 创建时间戳 | 文档+实际 |
| update_time | int/string | 更新时间戳 | 文档+实际 |
| remark | string | 用户备注 | 实际 |
| boss_remark | string | 管理员备注 | 实际 |

> ⚠️ 文档记录 `product_name`（float）和 `type_name`（string），但实际 API 不返回这些字段，而是返回 `product_info`（JSON）、`product_type`（int）等。实际 API 返回字段比文档更丰富。
> 响应 data 还含 `total` 总数。
