# Planet 监控接口

> 全局 Header: `Authorization: Bearer {access_token}`

---

## POST /console/planet/getInstanceCpu — CPU 使用率

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| uuid | string | 是 | 实例 UUID |
| product_type | string | 否 | 产品类型 |
| begin_date | string | 否 | 开始时间 |
| end_date | string | 否 | 结束时间 |

---

## POST /console/planet/getInstanceMemory — 内存使用率

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| uuid | string | 是 | 实例 UUID |
| product_type | string | 否 | 产品类型 |
| begin_date | string | 否 | 开始时间 |
| end_date | string | 否 | 结束时间 |

---

## POST /console/planet/getInstanceBlock — 磁盘使用率

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| uuid | string | 是 | 实例 UUID |
| product_type | string | 否 | 产品类型 |
| begin_date | string | 否 | 开始时间 |
| end_date | string | 否 | 结束时间 |

---

## POST /console/planet/getInstanceNetwork — 实例网络信息

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| uuid | string | 是 | 实例 UUID |
| product_type | string | 否 | 产品类型 |
| begin_date | string | 否 | 开始时间 |
| end_date | string | 否 | 结束时间 |

---

## POST /console/planet/getPlanetResources — 获取 Planet 资源

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| uuid | string | 是 | 实例 UUID |

**响应 data:**

| 字段 | 类型 | 说明 |
|------|------|------|
| list | array | 资源列表 |
| list[].uuid | string | 资源 UUID |
| list[].name | string | 资源名 |
| list[].type | string | 资源类型 |
| list[].type_name | string | 类型名 |
