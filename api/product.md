# 通用产品资源接口（ProductController）

> 全局 Header: `Authorization: Bearer {access_token}`
> 统一响应: `code=200` 正常

---

## POST /console/product/freed — 释放资源（销毁实例）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| uuid | string | 是 | 实例 UUID |

---

## POST /console/product/getStatusByUuid — 查询资源状态

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| uuid | string | 是 | 实例 UUID |

**响应 data:**

| 字段 | 类型 | 说明 |
|------|------|------|
| status | int | 状态值 |

---

## POST /console/product/getUserAllProductList — 所有产品列表

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| begin_date | string | 否 | 开始日期 |
| end_date | string | 否 | 结束日期 |
| is_renew | int | 否 | 是否续费 |
| ctime_sort | int | 否 | 创建时间排序 |
| etime_sort | int | 否 | 到期时间排序 |
| page_num | int | 是 | 页码 |
| page_size | int | 是 | 每页条数 |
| name | string | 否 | 名称 |
| region_uuid | string | 否 | 区域 |
| product_type | int | 否 | 产品类型 |

**响应 data.list[]:**

uuid, is_renew, name, region_uuid, city_name, city_code, status, create_time, end_time, billing_model, service_period

> 响应 data 还含 `total` 总数。

---

## POST /console/product/changeName — 修改名称

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| uuid | string | 是 | 实例 UUID |
| name | string | 是 | 新名称 |
| remark | string | 否 | 备注 |

---

## POST /console/product/changeProject — 迁移项目组

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| uuid | string | 是 | 实例 UUID |
| project_uuid | string | 是 | 目标项目 UUID |

---

## POST /console/product/serUserProductRenew — 设置自动续费

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| uuid | string | 是 | 实例 UUID |
| is_renew | int | 是 | 1-续费 0-不续费 |

---

## POST /console/product/addRenew — 续费

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| uuid | string | 是 | 实例 UUID |
| service_period | int | 是 | 续费周期 |
| coupon_id | int | 否 | 优惠券 |
| user_time | int | 否 | 时长 |
| remark | string | 否 | 备注 |

---

## POST /console/product/getRenewPrice — 续费价格

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| uuid | string | 是 | 实例 UUID |
| service_period | int | 是 | 续费周期 |
| coupon_id | int | 否 | 优惠券 |
| user_time | int | 否 | 时长 |
| remark | string | 否 | 备注 |

**响应 data:**

| 字段 | 类型 | 说明 |
|------|------|------|
| total_price | float | 总价 |
| original_price | float | 原价 |
| discount_price | float | 折扣价 |
| coupon_price | float | 优惠券抵扣 |

---

## POST /console/product/getProductType — 产品分类列表

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| product_type | int | 否 | 产品类型筛选 |

**响应 data:** category_uuid, name, status, product_type, description, flag_code, billing_model, service_period

---

## POST /console/product/getRegion — 区域列表

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| category_uuid | string | 是 | 分类 UUID |

**响应 data:** id, name, children(id, name, country, coordinate, flag_code, zone[], region_id, status, city_code, system_disk_interval, data_disk_interval, backup_open_status)

---

## POST /console/product/getAllImageType — 所有镜像类型

无请求参数。

**响应 data:** id, name, type, icon_type, create_time, update_time
