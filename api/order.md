# 订单接口（OrderController）

> 全局 Header: `Authorization: Bearer {access_token}`
> 统一响应: `code=200` 正常

---

## POST /console/order/list — 订单列表

**Body:**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page_num | int | 是 | 页码 |
| page_size | int | 是 | 每页条数 |
| status | int | 否 | 状态: 0-未支付 1-已支付 2-已取消 3-已退款 |
| product_type | int | 否 | 产品类型: 1-ECS 2-BareMetal 3-CDN |
| begin_date | string | 否 | 开始日期 |
| end_date | string | 否 | 结束日期 |
| is_renew | int | 否 | 是否续费 |
| ctime_sort | int | 否 | 创建时间排序 |
| etime_sort | int | 否 | 到期时间排序 |

**响应 data.list[]:**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 订单 ID |
| order_sn | string | 订单号 |
| payid | int | 支付 ID |
| status | int | 0-未支付 1-已支付 2-已取消 3-已退款 |
| type | int | 1-新购 2-续费 3-升级 |
| product_type | int | 1-ECS 2-BareMetal 3-CDN |
| product_info | string | 产品信息 JSON |
| original_price | float | 原价 |
| amount | float | 实付金额 |
| discount | float | 折扣 |
| ctime | string | 创建时间 |
| utime | string | 更新时间 |
| remark | string | 用户备注 |
| boss_remark | string | 管理员备注 |

> 响应 data 还含 `total` 总数。
