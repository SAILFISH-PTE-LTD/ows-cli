# ows SDK Reference

Auto-generated from source docstrings.  Run `python scripts/generate_sdk_doc.py` to update.

## Quick Start

```python
from ows.client import OwsClient

# From config file
client = OwsClient.from_config("config.json")

# From environment variables (OWS_APP_ID / OWS_APP_SECRET)
client = OwsClient.from_config()   # config.json not found → env vars
```

## PlanetAPI

API client for Planet (VPS) management operations.

Provides methods for instance lifecycle management including
creation, listing, detail retrieval, and power operations.

### `create`

Create a new Planet (VPS) instance.

```python
PlanetAPI.create(req: CreateRequest) → CreateResult
```


| Parameter | Description |
| --- | --- |
| **req** (CreateRequest) | Creation request with region, image, flavor, and password. |


**Returns:**
- Result with uuid (may be empty — creation is async).

### `get_detail`

Get full instance detail by UUID.

```python
PlanetAPI.get_detail(uuid: str, project_uuid: str = None) → InstanceDetail
```


| Parameter | Description |
| --- | --- |
| **uuid** (str) | Instance UUID. |
| **project_uuid** (str, default=None) | Optional project UUID filter. |


**Returns:**
- Full instance detail including network and disk information.

### `get_flavor_by_add`

List available instance flavors in a region/category.

```python
PlanetAPI.get_flavor_by_add(region_uuid: str, category_uuid: str) → list[Flavor]
```


| Parameter | Description |
| --- | --- |
| **region_uuid** (str) | Region UUID. |
| **category_uuid** (str) | Product category UUID. |


### `get_image_by_region`

List available OS images in a region.

```python
PlanetAPI.get_image_by_region(region_uuid: str, is_self: int = 0) → list[Image]
```


| Parameter | Description |
| --- | --- |
| **region_uuid** (str) | Region UUID to query images for. |
| **is_self** (int, default=0) | Filter for self-owned images (0=all, 1=self only). |


### `get_planet_type`

List product categories (Shared vCPU, Dedicated vCPU, Bare Metal).

```python
PlanetAPI.get_planet_type() → list[PlanetType]
```


### `get_price`

Calculate configuration price.

```python
PlanetAPI.get_price(req: PriceRequest) → PriceResult
```


| Parameter | Description |
| --- | --- |
| **req** (PriceRequest) | Price calculation request with region, flavor, and billing parameters. |


**Returns:**
- Calculated price details.

### `list_instances`

List Planet instances with optional filters.

```python
PlanetAPI.list_instances(req: ListRequest = None) → ListResult[Instance]
```


| Parameter | Description |
| --- | --- |
| **req** (ListRequest, default=None) | Optional filter/pagination request. Defaults to empty ListRequest. |


### `reboot`

Reboot an instance.

```python
PlanetAPI.reboot(uuid: str, reboot_type: int) → NoneType
```


| Parameter | Description |
| --- | --- |
| **uuid** (str) | Instance UUID. |
| **reboot_type** (int) | Reboot type (0=soft reboot, 1=hard reboot). |


### `start`

Start a stopped instance.

```python
PlanetAPI.start(uuid: str) → NoneType
```


| Parameter | Description |
| --- | --- |
| **uuid** (str) | Instance UUID. |


### `stop`

Stop a running instance.

```python
PlanetAPI.stop(uuid: str) → NoneType
```


| Parameter | Description |
| --- | --- |
| **uuid** (str) | Instance UUID. |


## ProductAPI

API client for general product operations.

Provides methods for resource lifecycle operations including
destruction, status queries, and region lookup.

### `free`

Permanently destroy (free) a resource.

```python
ProductAPI.free(uuid: str) → NoneType
```


| Parameter | Description |
| --- | --- |
| **uuid** (str) | Resource UUID to destroy. |


### `get_region`

List available regions with zone/city information.

```python
ProductAPI.get_region(category_uuid: str = '') → list[Region]
```


| Parameter | Description |
| --- | --- |
| **category_uuid** (str, default='') | Optional category UUID filter. Empty string returns all regions. |


### `get_status`

Check resource status by UUID.

```python
ProductAPI.get_status(uuid: str) → StatusResult
```


| Parameter | Description |
| --- | --- |
| **uuid** (str) | Resource UUID. |


**Returns:**
- Result with numeric status code.

## OrderAPI

API client for billing order operations.

Provides methods for listing and querying billing orders.

### `list_orders`

List billing orders / charge records.

```python
OrderAPI.list_orders(req: OrderListRequest = None) → ListResult[Order]
```


| Parameter | Description |
| --- | --- |
| **req** (OrderListRequest, default=None) | Optional filter/pagination request. Defaults to empty OrderListRequest. |


## BillAPI

API client for billing operations.

Provides methods for querying billing and invoice details.

### `get_detail_by_month`

Get monthly bill breakdown by resource.

```python
BillAPI.get_detail_by_month(req: BillMonthRequest = None) → BillDetail
```


| Parameter | Description |
| --- | --- |
| **req** (BillMonthRequest, default=None) | Optional bill month request. Defaults to empty BillMonthRequest. |


**Returns:**
- Monthly bill details with per-resource breakdown.

## Models

### `ListResult`

Paginated list result.

| Field | Type | Default | Description |
| --- | --- | --- | --- |
| `list` | list[T] | *(required)* | Items for the current page. |
| `total` | int | 0 | Total number of matching items across all pages. |


### `StatusResult`

Resource status result.

| Field | Type | Default | Description |
| --- | --- | --- | --- |
| `status` | int | *(required)* | Status code (0=Deleted, 1=Running, 3=Suspend, 4=Down, 16=Creating, 106=Executing). |


### `CreateResult`

Create operation result.

| Field | Type | Default | Description |
| --- | --- | --- | --- |
| `uuid` | str | *(required)* | Instance UUID.  May be empty — creation is asynchronous. |


### `PlanetType`

Product category.

| Field | Type | Default | Description |
| --- | --- | --- | --- |
| `category_uuid` | str | *(required)* | Category UUID. |
| `name` | str | *(required)* | Display name (e.g. "Shared vCPU"). |
| `status` | int | *(required)* | Category status. |
| `product_type` | int | 0 | Product type code. |
| `description` | str | "" | Category description. |
| `flag_code` | str | "" | Region flag code. |
| `billing_model` | str | "" | Supported billing models. |
| `service_period` | int | 0 | Service period (months). |


### `Image`

OS image group.

| Field | Type | Default | Description |
| --- | --- | --- | --- |
| `id` | int | *(required)* | Image group ID. |
| `name` | str | *(required)* | Group name (e.g. "Ubuntu"). |
| `icon_type` | str | "" | Icon type label. |
| `type` | int | 0 | Image type code. |
| `images` | list | (factory) | List of image dicts (``name``, ``uuid``, ``id``). |


### `Flavor`

Instance specification (vCPU + memory).

| Field | Type | Default | Description |
| --- | --- | --- | --- |
| `uuid` | str | *(required)* | Flavor UUID. |
| `name` | str | *(required)* | Human-readable name ("1C-2G"). |
| `id` | int | 0 | Flavor ID. |
| `cores` | int | 0 | vCPU count. |
| `memory` | int | 0 | Memory in GB. |
| `h_price` | float | 0.0 | Hourly price (USD). |
| `m_price` | float | 0.0 | Monthly price (USD). |
| `h_discount_price` | float | 0.0 | Discounted hourly price. |
| `m_discount_price` | float | 0.0 | Discounted monthly price. |
| `free_flow` | int | 0 | Included free traffic. |
| `status` | int | 0 | Availability status. |


### `DataDisk`

Additional data disk specification.

| Field | Type | Default | Description |
| --- | --- | --- | --- |
| `name` | str | "" | Disk display name. |
| `disk_size` | int | 0 | Size in GB. |
| `disk_type` | int | 0 | Disk type code (1=SSD). |


### `PriceRequest`

Parameters for :meth:`PlanetAPI.get_price`.

| Field | Type | Default | Description |
| --- | --- | --- | --- |
| `region_uuid` | str | *(required)* | Region UUID. |
| `flavor_uuid` | str | *(required)* | Flavor UUID. |
| `image_uuid` | str | *(required)* | Image UUID. |
| `system_disk` | int | *(required)* | System disk size (GB). |
| `billing_model` | int | *(required)* | ``1`` = monthly, ``2`` = pay-as-you-go. |
| `service_period` | int | *(required)* | Duration (months for billing_model=1; ``1`` for billing_model=2). |
| `data_disk` | list[DataDisk] | (factory) | Additional data disks. |
| `coupon_id` | int | 0 | Coupon ID (0 = none). |
| `user_time` | int | 0 | Purchase duration override (0 = default). |


### `PriceResult`

Price breakdown returned by :meth:`PlanetAPI.get_price`.

| Field | Type | Default | Description |
| --- | --- | --- | --- |
| `flavor_price` | float | 0.0 | Flavor base price. |
| `system_disk_price` | float | 0.0 | System disk price. |
| `data_disk_price` | float | 0.0 | Data disk total price. |
| `flow_price` | float | 0.0 | Traffic price. |
| `ip_price` | float | 0.0 | IP address price. |
| `image_price` | float | 0.0 | Image price. |
| `total_price` | float | 0.0 | Total after discounts and coupons. |
| `original_price` | float | 0.0 | Original total before discounts. |
| `discount_price` | float | 0.0 | Discount amount. |
| `coupon_price` | float | 0.0 | Coupon amount. |


### `CreateRequest`

Parameters for :meth:`PlanetAPI.create`.

| Field | Type | Default | Description |
| --- | --- | --- | --- |
| `region_uuid` | str | *(required)* | Region UUID. |
| `flavor_uuid` | str | *(required)* | Flavor UUID. |
| `image_uuid` | str | *(required)* | Image UUID. |
| `system_disk` | int | *(required)* | System disk size (GB). |
| `billing_model` | int | *(required)* | ``1`` = monthly, ``2`` = pay-as-you-go. |
| `service_period` | int | *(required)* | Duration (months or ``1``). |
| `project_uuid` | str | "" | Project UUID. |
| `name` | str | "" | Instance display name; auto-generated if empty. |
| `data_disk` | list[DataDisk] | (factory) | Additional data disks. |
| `remark` | str | "" | Remark / note. |
| `adminPass` | str | "" | Admin password.  Auto-generated if empty. Must contain upper + lower + digit + special. |
| `ssh_key` | str | "" | SSH public key. |
| `security_group_uuid` | str | "" | Security group UUID. |
| `coupon_id` | int | 0 | Coupon ID. |
| `user_time` | int | 0 | Purchase duration override. |
| `is_renew` | int | 0 | Auto-renew flag. |
| `is_backup` | int | 0 | Backup flag. |
| `app_market_uuid` | str | "" | Application market image UUID. |
| `app_market_base_data` | str | "" | Application market base data. |


### `ListRequest`

Parameters for :meth:`PlanetAPI.list_instances`.

| Field | Type | Default | Description |
| --- | --- | --- | --- |
| `page_num` | int | 1 | Page number (1-indexed). |
| `page_size` | int | 10 | Items per page. |
| `region_uuid` | str | "" | Filter by region UUID. |
| `project_uuid` | str | "" | Filter by project UUID. |
| `begin_date` | str | "" | Filter by start date. |
| `end_date` | str | "" | Filter by end date. |
| `status` | str | "" | Filter by status string. |
| `ctime_sort` | int | 0 | Sort by creation time. |
| `etime_sort` | int | 0 | Sort by end time. |
| `name` | str | "" | Filter by instance name. |
| `ip` | str | "" | Filter by IP address. |
| `keyword` | str | "" | Keyword search. |
| `app_market_type` | str | "" | Application market type filter. |


### `Instance`

Instance summary (returned by :meth:`PlanetAPI.list_instances`).

| Field | Type | Default | Description |
| --- | --- | --- | --- |
| `uuid` | str | "" | Instance UUID. |
| `sid` | int | 0 | - |
| `uid` | int | 0 | - |
| `flavor_name` | str | "" | Flavor name ("1C-2G", ...). |
| `flavor_uuid` | str | "" | - |
| `model` | str | "" | - |
| `model_id` | int | 0 | - |
| `cores` | str | "" | - |
| `memory` | str | "" | - |
| `storage` | str | "" | - |
| `nic` | str | "" | - |
| `gpu` | str | "" | - |
| `name` | str | "" | Display name. |
| `host` | str | "" | - |
| `region_uuid` | str | "" | Region UUID. |
| `region_name` | str | "" | - |
| `region_id` | int | 0 | - |
| `city_name` | str | "" | City name. |
| `city_code` | str | "" | City code ("SIN", "TPE", ...). |
| `status` | int | 0 | Numeric status code. |
| `status_name` | str | "" | Human-readable status. |
| `system_type` | int | 0 | - |
| `create_time` | str | "" | Creation timestamp string. |
| `stop_time` | int | 0 | - |
| `delete_time` | int | 0 | - |
| `end_time` | int | 0 | Expiration Unix timestamp. |
| `private_ip` | list | (factory) | - |
| `public_ip` | str | "" | Public IPv4 address. |
| `public_ipv6` | str | "" | - |
| `image_id` | int | 0 | - |
| `image_name` | str | "" | - |
| `image_uuid` | str | "" | - |
| `os_icon_type` | str | "" | - |
| `project_uuid` | str | "" | - |
| `billing_model` | int | 0 | - |
| `service_period` | int | 0 | - |
| `amount` | int | 0 | - |
| `bandwidth_cap` | int | 0 | - |
| `speed_type` | int | 0 | - |
| `is_enable_security_group` | int | 0 | - |
| `is_own` | int | 0 | - |
| `product_type` | int | 0 | - |
| `app_market_type` | str | "" | - |
| `email` | str | "" | - |
| `username` | str | "" | - |
| `data_disk` | list | (factory) | - |


### `InstanceDetail`

Full instance detail (returned by :meth:`PlanetAPI.get_detail`).

| Field | Type | Default | Description |
| --- | --- | --- | --- |
| `uuid` | str | "" | Instance UUID. |
| `region_uuid` | str | "" | Region UUID. |
| `image_uuid` | str | "" | Image UUID. |
| `flavor_uuid` | str | "" | Flavor UUID. |
| `flavor_name` | str | "" | Flavor name. |
| `cores` | str | "" | vCPU count (str from API). |
| `memory` | str | "" | Memory in GB (str from API). |
| `storage` | str | "" | Storage size (str from API). |
| `nic` | str | "" | - |
| `gpu` | str | "" | GPU info (empty if none). |
| `name` | str | "" | Display name. |
| `system_type` | str | "" | - |
| `city_name` | str | "" | City name. |
| `city_code` | str | "" | City code. |
| `public_ip` | str | "" | Public IPv4 address. |
| `status` | int | 0 | Numeric status code. |
| `status_name` | str | "" | Human-readable status. |
| `create_time` | str | "" | Creation time string. |
| `end_time` | str | "" | Expiration Unix timestamp. |
| `project_uuid` | str | "" | Project UUID. |
| `free_flow` | int | 0 | - |
| `is_backup` | int | 0 | - |
| `backup_open_status` | int | 0 | - |
| `private_port` | dict | (factory) | Internal port info dict. |
| `public_port` | dict | (factory) | Dict with ``ip`` and ``port`` keys. |
| `data_disk` | list | (factory) | Data disk list. |
| `subnet` | list | (factory) | Subnet list. |
| `security_group` | list | (factory) | Security group list. |
| `app_market` | list | (factory) | - |


### `Order`

Billing order / charge record.

| Field | Type | Default | Description |
| --- | --- | --- | --- |
| `id` | int | 0 | Order ID. |
| `uid` | int | 0 | - |
| `order_sn` | str | "" | Order serial number. |
| `payid` | int | 0 | - |
| `status` | int | 0 | Order status (0=Not Paid, 1=Paid, 2=Expired, 3=Deleted). |
| `type` | int | 0 | Order type. |
| `product_type` | int | 0 | Product type code. |
| `product_info` | str | "" | - |
| `original_price` | float | 0.0 | Original price before discount. |
| `amount` | float | 0.0 | Order amount (USD). |
| `discount` | float | 0.0 | Discount amount. |
| `ctime` | str | "" | Creation time string. |
| `utime` | str | "" | Update time string. |
| `create_time` | int | 0 | - |
| `update_time` | int | 0 | - |
| `delete_time` | int | 0 | - |
| `remark` | str | "" | User remark. |
| `boss_remark` | str | "" | Administrator remark. |


### `OrderListRequest`

Parameters for :meth:`OrderAPI.list_orders`.

| Field | Type | Default | Description |
| --- | --- | --- | --- |
| `page_num` | int | 1 | Page number (1-indexed). |
| `page_size` | int | 10 | Items per page. |
| `status` | int | 0 | Order status filter (0=Not Paid, 1=Paid, 2=Expired, 3=Deleted). |
| `product_type` | int | 0 | Product type filter. |
| `begin_date` | str | "" | Start date string ("" = no filter). |
| `end_date` | str | "" | End date string ("" = no filter). |
| `time_sort` | int | 0 | Sort by time. |
| `price_sort` | int | 0 | Sort by price. |


### `BillItem`

Single line item in a monthly bill.

| Field | Type | Default | Description |
| --- | --- | --- | --- |
| `sid` | int | 0 | Instance ID (0 for non-instance items like traffic). |
| `region_id` | int | 0 | Region ID. |
| `total_money` | str | '0' | Cost in USD (string from API). |
| `start_time` | int | 0 | Billing start Unix timestamp. |
| `end_time` | int | 0 | Billing end Unix timestamp. |
| `total` | int | 0 | Billing duration (10-min units). |
| `quantity` | int | 0 | Billing quantity. |
| `display_value` | str | '0' | - |
| `max_quantity` | int | 0 | - |
| `type` | int | 0 | Item type (1=Instance, 2=Traffic). |
| `server_end_time` | int | 0 | - |
| `product_info` | str | "" | - |
| `name` | str | "" | Instance name. |
| `product_type` | int | 0 | - |
| `product_name` | str | "" | Product type name ("ECS"). |
| `ip` | str | "" | Instance IP address. |
| `region_name` | str | "" | Region display name. |
| `description` | str | "" | Item description. |


### `BillDetail`

Monthly bill detail.

| Field | Type | Default | Description |
| --- | --- | --- | --- |
| `list` | list[BillItem] | (factory) | Bill line items. |
| `invid` | str | "" | Invoice ID. |
| `user_total_money` | str | '0' | Total cost in USD. |
| `total_gift` | str | '0' | Total gift/credit. |


### `BillMonthRequest`

Parameters for :meth:`BillAPI.get_detail_by_month`.

| Field | Type | Default | Description |
| --- | --- | --- | --- |
| `begin_date` | str | "" | Billing period start (Unix timestamp string). |
| `end_date` | str | "" | Billing period end (Unix timestamp string). |
| `team_uuid` | str | "" | Team UUID ("" = default team). |


## Error Handling

- **`OwsError`** — Base exception for all ows errors.
- **`AuthError`** — Authentication failed — credentials invalid or token unusable.
- **`APIError`** — API returned a non-200 response code.
- **`NetworkError`** — HTTP connection or timeout error.

```python
from ows.errors import AuthError, APIError, NetworkError

try:
    client.planet.create(req)
except AuthError:
    print("Credentials invalid or expired")
except APIError as e:
    print(f"API error [{e.code}]: {e.message}")
except NetworkError:
    print("Network connection failed")
```


## CLI

For CLI usage, run `ows --help` or see the README.
