# Planet 查询/信息接口

> 全局 Header: `Authorization: Bearer {access_token}`
> 统一响应: `code=200` 正常, `code=110` 未登录

---

## POST /console/planet/getPlanetType — 产品分类列表

无请求参数。

**响应 data:**

| 字段 | 类型 | 说明 |
|------|------|------|
| category_uuid | string | 分类 UUID |
| name | string | 名称 |
| status | int | 1-显示 2-不显示 3-售罄 |
| product_type | int | 产品类型 |
| description | string | 描述 |
| flag_code | string | 图标代码 |
| billing_model | string | 计费: 1-订阅 2-按量 |
| service_period | int | 服务周期 |

---

## POST /console/planet/getImageByRegion — 获取镜像列表

**Body:**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| region_uuid | string | 是 | 区域 UUID |
| is_self | int | 是 | 是否自有镜像 |

**响应 data:**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 镜像 ID |
| name | string | 镜像名 |
| icon_type | string | 图标类型 |
| images | string | 镜像 URL |
| uuid | string | 镜像 UUID |

---

## POST /console/planet/getFlavorByAdd — 可创建规格

**Body:**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| region_uuid | string | 是 | 区域 UUID |
| category_uuid | string | 是 | 分类 UUID |

**响应 data:**

| 字段 | 类型 | 说明 |
|------|------|------|
| uuid | string | 规格 UUID |
| name | string | 规格名 |
| cores | string | CPU 核数 |
| memory | string | 内存 |
| storage | string | 存储 |
| nic | string | 网卡 |
| gpu | string | GPU |
| h_price | float | 时价 |
| m_price | float | 月价 |
| h_discount_price | float | 时折扣价 |
| free_flow | int | 免费流量 |
| status | int | 状态 |

---

## POST /console/planet/getFlavorByAdjust — 可调整规格

**Body:**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| region_uuid | string | 是 | 区域 UUID |
| uuid | string | 是 | 当前实例 UUID |

**响应 data:** 同 getFlavorByAdd

---

## POST /console/planet/getPrice — 计算配置价格

**Body:**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| region_uuid | string | 是 | 区域 UUID |
| flavor_uuid | string | 是 | 规格 UUID |
| image_uuid | string | 是 | 镜像 UUID |
| system_disk | int | 是 | 系统盘大小 (GB) |
| data_disk | array | 否 | 数据盘 [{name, disk_size, disk_type}] |
| coupon_id | int | 否 | 优惠券 ID |
| user_time | int | 否 | 购买时长 |
| billing_model | int | 是 | 计费模式 |
| service_period | int | 是 | 服务周期 |

**响应 data:**

| 字段 | 类型 | 说明 |
|------|------|------|
| flavor_price | float | 规格价格 |
| system_disk_price | float | 系统盘价格 |
| data_disk_price | float | 数据盘价格 |
| flow_price | float | 流量价格 |
| ip_price | float | IP 价格 |
| image_price | float | 镜像价格 |
| total_price | float | 总价 |
| original_price | float | 原价 |
| discount_price | float | 折扣价 |
| coupon_price | float | 优惠券抵扣 |

---

## POST /console/planet/getAppMarket — 获取应用镜像

**Body:**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| region_uuid | string | 是 | 区域 UUID |

**响应 data:**

| 字段 | 类型 | 说明 |
|------|------|------|
| list | array | 应用列表 |
| list[].uuid | string | 应用 UUID |
| list[].name | string | 应用名称 |
