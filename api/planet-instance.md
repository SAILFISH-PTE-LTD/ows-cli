# Planet 实例生命周期管理

> 全局 Header: `Authorization: Bearer {access_token}`
> 统一响应格式: `code=200` 正常，未登录=110

---

## POST /console/planet/add — 创建实例

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| region_uuid | string | 是 | 区域 |
| flavor_uuid | string | 是 | 规格 |
| image_uuid | string | 是 | 镜像 |
| project_uuid | int | 否 | 项目 |
| system_disk | int | 是 | 系统盘 GB |
| data_disk | array | 否 | [{name, disk_size, disk_type}] |
| remark | string | 否 | 备注 |
| adminPass | string | 否 | 管理员密码 |
| ssh_key | string | 否 | SSH 公钥 |
| security_group_uuid | string | 否 | 安全组 |
| coupon_id | int | 否 | 优惠券 |
| user_time | int | 否 | 购买时长 |
| billing_model | int | 是 | 计费模式 |
| service_period | int | 是 | 服务周期 |
| is_renew | int | 否 | 自动续费 |
| is_backup | int | 否 | 开启备份 |
| app_market_uuid | string | 否 | 应用市场镜像 |
| app_market_base_data | string | 否 | 应用配置数据 |

---

## POST /console/planet/list — 实例列表

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| region_uuid | string | 否 | 区域 |
| project_uuid | string | 否 | 项目 |
| begin_date | string | 否 | 开始日期 |
| end_date | string | 否 | 结束日期 |
| status | string | 否 | 状态 |
| ctime_sort | int | 否 | 创建时间排序 |
| etime_sort | int | 否 | 到期时间排序 |
| name | string | 否 | 名称 |
| ip | string | 否 | IP |
| keyword | string | 否 | 关键词 |
| app_market_type | string | 否 | 应用类型 |
| page_num | int | 是 | 页码 |
| page_size | int | 是 | 每页条数 |

**响应 data.list[]:**

| 字段 | 类型 | 说明 |
|------|------|------|
| uuid | string | UUID |
| flavor_name | string | 规格名 |
| model | string | 型号 |
| cores | string | CPU |
| memory | string | 内存 |
| storage | string | 存储 |
| nic | string | 网卡 |
| gpu | string | GPU |
| name | string | 实例名 |
| region_uuid/region_name | string | 区域 |
| status/status_name | int/string | 状态 |
| create_time | string | 创建时间 |
| private_ip/public_ip/public_ipv6 | string | IP |
| image_name | string | 镜像名 |
| os_icon_type | string | 图标 |
| project_uuid | string | 项目 |
| billing_model | int | 计费模式 |
| service_period | int | 服务周期 |
| data_disk | array | 数据盘 |

> 响应 data 还含 `total` (int) 总数。

---

## POST /console/planet/getDetail — 实例详情

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| project_uuid | string | 否 | 项目 |
| uuid | string | 是 | 实例 UUID |

**响应 data（主字段）:**

uuid, region_uuid, image_uuid, flavor_uuid/name, cores, memory, storage, nic, gpu, name, system_type, city_name/code, status/status_name, create_time, end_time, project_uuid, free_flow, is_backup, backup_open_status, private_port, public_port, data_disk, subnet, security_group, app_market

---

## POST /console/planet/stop — 关机

| 字段 | 类型 | 必填 |
|------|------|------|
| uuid | string | 是 |

---

## POST /console/planet/start — 开机

| 字段 | 类型 | 必填 |
|------|------|------|
| uuid | string | 是 |

---

## POST /console/planet/reboot — 重启

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| uuid | string | 是 | 实例 UUID |
| reboot_type | int | 是 | 重启类型 |

---

## POST /console/planet/rebuild — 重装系统

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| uuid | string | 是 | 实例 UUID |
| image_uuid | string | 是 | 镜像 |
| new_password | string | 否 | 新密码 |
| app_market_uuid | string | 否 | 应用镜像 |
| app_market_base_data | string | 否 | 应用配置 |

---

## POST /console/planet/changePassword — 修改密码（仅 ECS）

| 字段 | 类型 | 必填 |
|------|------|------|
| uuid | string | 是 |
| new_password | string | 是 |

---

## POST /console/planet/adjustFlavor — 调整规格（仅 ECS）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| uuid | string | 是 | 实例 UUID |
| coupon_id | int | 否 | 优惠券 |
| user_time | int | 否 | 剩余时长 |
| flavor_uuid | string | 是 | 目标规格 |
| remark | string | 否 | 备注 |

---

## POST /console/planet/getAdjustFlavorPrice — 调整规格价格（仅 ECS）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| uuid | string | 是 | 实例 UUID |
| coupon_id | int | 否 | 优惠券 |
| user_time | int | 否 | 剩余时长 |
| flavor_uuid | string | 是 | 目标规格 |
| remark | string | 否 | 备注 |

---

## POST /console/planet/vncConsole — VNC 控制台（仅 ECS）

| 字段 | 类型 | 必填 |
|------|------|------|
| uuid | string | 是 |

**响应 data:**

| 字段 | 类型 | 说明 |
|------|------|------|
| type | string | 连接类型 |
| url | string | VNC URL |
