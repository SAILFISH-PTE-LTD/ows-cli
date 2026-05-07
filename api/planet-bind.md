# Planet 绑定与计费变更

> 全局 Header: `Authorization: Bearer {access_token}`

---

## POST /console/planet/getOperableInstance — 可绑定实例

获取可绑定数据盘或内网的实例列表。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| region_uuid | string | 是 | 区域 |
| uuid | string | 是 | 当前实例 UUID（排除自身） |

**响应 data:**

| 字段 | 类型 | 说明 |
|------|------|------|
| ins_id | int | 实例 ID |
| name | string | 实例名 |
| uuid | string | 实例 UUID |
| product_type | int | 产品类型 |

---

## POST /console/planet/applyGroup — 绑定安全组

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| sg_group_id | int | 是 | 安全组 ID |
| uuid | string | 是 | 实例 UUID |

---

## POST /console/planet/applyPrivateNetwork — 绑定内网

| 字段 | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| private_network_uuid | string | 是 | - | 内网 UUID |
| uuid | string | 是 | - | 实例 UUID |
| type | int | 否 | 1 | 绑定类型 |

---

## POST /console/planet/untiePlanet — 解绑 CIDR/BYOIP

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| planet_uuid | string | 是 | Planet UUID |
| uuid | string | 是 | CIDR/BYOIP UUID |
| child_cidr_uuid | string | 否 | 子 CIDR UUID |

---

## POST /console/planet/bindingPlanet — 绑定 CIDR/BYOIP

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| uuid | string | 是 | CIDR/BYOIP UUID |
| child_cidr_uuid | string | 否 | 子 CIDR UUID |
| planet_uuid | string | 是 | Planet UUID |
| ip | string | 否 | 指定 IP |

---

## POST /console/planet/convertToSubscription — 按量转订阅

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| uuid | string | 是 | 实例 UUID |
| coupon_id | string | 否 | 优惠券 ID |
| is_renew | int | 否 | 自动续费 |

---

## POST /console/planet/getConvertToSubscriptionPrice — 按量转订阅价格

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| uuid | string | 是 | 实例 UUID |
| coupon_id | string | 否 | 优惠券 ID |

**响应 data:**

| 字段 | 类型 | 说明 |
|------|------|------|
| total_price | float | 总价 |
| original_price | float | 原价 |
| discount_price | float | 折扣价 |
| coupon_price | float | 优惠券抵扣 |
