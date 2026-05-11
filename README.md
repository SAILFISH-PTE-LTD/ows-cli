# ows

CLI tool for managing VPS (Planet) instances on ows.us.

## Installation

```bash
pip install git+https://github.com/SAILFISH-PTE-LTD/ows-cli.git
```

For local development:

```bash
git clone git@github.com:SAILFISH-PTE-LTD/ows-cli.git
cd ows-cli
pip install -e .
```

Requires Python 3.10+.

## Authentication

Choose one of two methods. When both are present, the config file takes precedence.

### Method 1: Config File

Create a `config.json` in your working directory:

```json
{
  "app_id": "your_app_id",
  "app_secret": "your_app_secret"
}
```

Use `-c` to specify a different path:

```bash
ows -c /path/to/config.json planet list
```

Keep `config.json` in `.gitignore` — it contains secrets.

### Method 2: Environment Variables

```bash
export OWS_APP_ID="your_app_id"
export OWS_APP_SECRET="your_app_secret"
```

Windows (PowerShell):

```powershell
$env:OWS_APP_ID = "your_app_id"
$env:OWS_APP_SECRET = "your_app_secret"
```

## Readable Identifiers

Instead of UUIDs, most commands accept human-readable values.

### Region

`--region` accepts any of the following:

| Form | Example | How it resolves |
|------|---------|----------------|
| City code | `SIN`, `TPE`, `MNL` | Exact match on `city_code` |
| Region name | `Singapore`, `Tokyo`, `Taipei` | Substring match on region name |
| UUID | `b8f2...` | Used directly |

Run `ows product regions` to see all available regions and their city codes.

### Flavor (Spec)

`--flavor-type` accepts a numeric code or `--flavor` accepts a name:

| Code | Name | vCPU | RAM |
|------|------|------|-----|
| 0 | `1C-2G` | 1 | 2 GB |
| 1 | `2C-4G` | 2 | 4 GB |
| 2 | `2C-8G` | 2 | 8 GB |
| 3 | `4C-8G` | 4 | 8 GB |
| 4 | `4C-16G` | 4 | 16 GB |
| 5 | `8C-16G` | 8 | 16 GB |
| 6 | `8C-32G` | 8 | 32 GB |
| 7 | `16C-32G` | 16 | 32 GB |
| 8 | `16C-64G` | 16 | 64 GB |

Default: `0` (1C-2G). Run `ows planet flavors --region SIN` to see all flavors in a region.

### Category (Product Type)

`--category-type` or category name:

| Code | Name |
|------|------|
| 0 | Shared vCPU |
| 1 | Dedicated vCPU |
| 2 | Bare Metal |

Default: `0`. Run `ows planet types` to list available categories.

### Image (OS)

`--image-type` accepts a numeric code or `--image` accepts a name:

| Code | Name |
|------|------|
| 0 | Ubuntu 20.04 |
| 1 | Ubuntu 18.04 |
| 2 | Ubuntu 22.04 |
| 3 | Ubuntu 24.04 |
| 4 | Debian 10 |
| 5 | Debian 11 |
| 6 | Debian 12 |
| 7 | Debian 13 |
| 8 | CentOS 7.3 |
| 9 | CentOS 7.5 |
| 10 | CentOS 7.6 |
| 11 | CentOS 7.9 |
| 12 | CentOS 8 Stream |
| 13 | CentOS 9 Stream |
| 14 | Rocky 9 |
| 15 | Rocky 10 |
| 16 | AlmaLinux OS 9 |
| 17 | AlmaLinux OS 10 |
| 18 | Windows 10 Pro |
| 19 | Windows 2012 R2 Standard |
| 20 | Windows 2016 Standard |
| 21 | Windows 2019 Standard |

Default: `0` (Ubuntu 20.04). Run `ows planet images --region SIN` to list what's available.

### Instance Reference

Most instance commands accept UUID, name, or IP interchangeably:

| Form | Example | How it finds |
|------|---------|-------------|
| UUID | `b8f2c1e0-...` | Direct lookup |
| Name | `Planet-SIN-abc123` | Exact API search |
| IP | `1.2.3.4` | Exact IP match |

---

## CLI Reference

All commands support `--json` for machine-readable output. Append `--json` to any command.

Global options:

```
-c, --config FILE   Config file path (default: config.json)
--json              Output as JSON
--help              Show help
```

### ows product regions

List all available regions.

```bash
ows product regions
ows product regions --category <UUID>   # filter by product category
```

### ows planet types

List product categories.

```bash
ows planet types
```

Output columns: Type code, Name, Category UUID, Status, Billing model.

### ows planet flavors

List available instance specs in a region.

```bash
ows planet flavors --region SIN
ows planet flavors --region Tokyo --category-type 1   # Dedicated vCPU only
```

**Options:**

| Option | Default | Description |
|--------|---------|-------------|
| `--region` | *(required)* | City code, region name, or UUID |
| `--category-type` | `0` | 0=Shared vCPU, 1=Dedicated vCPU, 2=Bare Metal |

### ows planet images

List available OS images in a region.

```bash
ows planet images --region SIN
ows planet images --region Tokyo --self 1   # self-owned images
```

**Options:**

| Option | Default | Description |
|--------|---------|-------------|
| `--region` | *(required)* | City code, region name, or UUID |
| `--self` | `0` | 1 = show self-owned images |

### ows planet price

Estimate configuration cost before creating.

```bash
# Default config (1C-2G, Ubuntu 20.04, 40GB, hourly)
ows planet price --region SIN

# Custom specs
ows planet price --region TPE --flavor-type 1 --image-type 2

# Monthly billing with data disk
ows planet price --region SIN --billing-model 1 --data-disk-json '[{"name":"data","disk_size":100,"disk_type":1}]'
```

**Options:**

| Option | Default | Description |
|--------|---------|-------------|
| `--region` | *(required)* | Region |
| `--flavor-type` | `0` | Flavor type code (0-8) |
| `--image-type` | `0` | Image type code (0-21) |
| `--flavor` | — | Flavor UUID or name (overrides `--flavor-type`) |
| `--image` | — | Image UUID or name (overrides `--image-type`) |
| `--system-disk` | `40` | System disk size (GB) |
| `--billing-model` | `2` | 1=monthly, 2=pay-as-you-go |
| `--service-period` | `1` | Months (for monthly) or 1 (for hourly) |
| `--coupon-id` | `0` | Coupon ID |
| `--user-time` | `0` | Purchase duration override |
| `--data-disk-json` | `[]` | JSON array of `{name, disk_size, disk_type}` |

### ows planet create

Create a new VPS instance.

```bash
# Minimal — picks defaults: 1C-2G, Ubuntu 20.04, auto password, auto name
ows planet create --region SIN

# With readable identifiers
ows planet create --region Tokyo --flavor 2C-4G --image "Debian 12"

# Custom name and password
ows planet create --region SIN --name my-vps --admin-pass "MyP@ssw0rd!"
ows planet create --region TPE --project my-project --remark "production"

# Monthly billing, blocked until deployment completes
ows planet create --region MNL --billing-model 1 --service-period 3
```

**Options:**

| Option | Default | Description |
|--------|---------|-------------|
| `--region` | *(required)* | Region (city code, name, or UUID) |
| `--flavor-type` | `0` | Flavor type code (0-8) |
| `--image-type` | `0` | Image type code (0-21) |
| `--flavor` | — | Flavor UUID or name |
| `--image` | — | Image UUID or name |
| `--system-disk` | `40` | System disk size (GB) |
| `--billing-model` | `2` | 1=monthly, 2=pay-as-you-go |
| `--service-period` | `1` | Duration |
| `--project` | `metro` | Project UUID or name |
| `--name` | auto | Instance name (auto: `Planet-{city}-{random}`) |
| `--admin-pass` | auto | Admin password (auto-generated, 16 chars) |
| `--ssh-key` | — | SSH public key |
| `--remark` | — | Remark / note |
| `--is-renew` | `0` | Auto-renew flag |
| `--is-backup` | `0` | Backup flag |
| `--data-disk-json` | `[]` | Additional data disks |
| `--no-wait` | — | Return immediately, don't wait for provisioning |

Password rules: must contain uppercase + lowercase + digit + special character.

### ows planet list

List your instances.

```bash
ows planet list
ows planet list --region SIN
ows planet list --page 1 --size 50
ows planet list --name my-vps
ows planet list --ip 1.2.3.4
ows planet list --status 1        # Running only
```

**Options:**

| Option | Default | Description |
|--------|---------|-------------|
| `--region` | — | Filter by region |
| `--page` | `1` | Page number |
| `--size` | `20` | Items per page |
| `--name` | — | Filter by name |
| `--ip` | — | Filter by IP |
| `--status` | — | Filter by status code |

### ows planet detail

Show full detail for an instance.

```bash
ows planet detail <UUID>
ows planet detail my-vps
ows planet detail 1.2.3.4
```

### ows planet start / stop / reboot

```bash
ows planet start  my-vps
ows planet stop   1.2.3.4
ows planet reboot <UUID> 0    # 0 = soft reboot, 1 = hard reboot
```

### ows product free

Permanently destroy an instance.

```bash
ows product free my-vps
ows product free 1.2.3.4
```

### ows product status

Check instance status by UUID, name, or IP.

```bash
ows product status my-vps
```

### ows order billing

List billing / charge records.

```bash
ows order billing
ows order billing --status 1           # Paid only
ows order billing --page 1 --page-size 50
ows order billing --begin-date 2026-05-01 --end-date 2026-05-31
```

**Options:**

| Option | Default | Description |
|--------|---------|-------------|
| `--status` | `0` | 0=Not Paid, 1=Paid, 2=Expired, 3=Deleted |
| `--product-type` | `0` | Product type filter |
| `--page` | `1` | Page number |
| `--page-size` | `20` | Items per page |
| `--begin-date` | — | YYYY-MM-DD |
| `--end-date` | — | YYYY-MM-DD |
| `--sort-time` | `0` | Sort by time |
| `--sort-price` | `0` | Sort by price |

### ows order detail

Monthly bill breakdown by resource.

```bash
ows order detail --month 2026-05
ows order detail --month 2026-05 --team-uuid <UUID>
```

---

## Instance Status Codes

| Code | Status |
|------|--------|
| 0 | Deleted |
| 1 | Running |
| 3 | Suspend (unpaid) |
| 4 | Down (stopped) |
| 16 | Creating |
| 106 | Executing |

---

## JSON Output

Every command supports `--json` for structured output:

```bash
# Filter with jq
ows planet list --json | jq '.list[] | {name, public_ip}'

# Scripts
ows planet create --region SIN --no-wait --json
# → {"uuid": null, "name": "Planet-SIN-abc123", "password": "...", "status": "provisioning"}
```

---

## Python SDK

You can use `ows` programmatically as a Python library.

### Quick Start

```python
from ows.client import OwsClient

# From config file
client = OwsClient.from_config("config.json")

# Or from environment variables (OWS_APP_ID / OWS_APP_SECRET)
import os
os.environ["OWS_APP_ID"] = "..."
os.environ["OWS_APP_SECRET"] = "..."
client = OwsClient.from_config()  # no args → tries env vars if config.json missing
```

### Query Regions

```python
regions = client.product.get_region()
for r in regions:
    print(r.name)
    for child in r.children:
        for zone in child.get("zone", []):
            print(f"  {child.get('name')} — {zone.get('city_code')} — {zone.get('region_uuid')}")
```

### Query Types, Flavors, Images

```python
# Product categories
types = client.planet.get_planet_type()
for t in types:
    print(f"{t.name} → {t.category_uuid}")

# Flavors in a region
flavors = client.planet.get_flavor_by_add(region_uuid="...", category_uuid="...")
for f in flavors:
    print(f"{f.name}: {f.cores}c{f.memory}g — ${f.h_price}/h, ${f.m_price}/m")

# Images in a region
images = client.planet.get_image_by_region(region_uuid="...")
for group in images:
    print(group.name)
    for img in group.images:
        print(f"  {img.get('name')} → {img.get('uuid')}")
```

### Price Estimate

```python
from ows.models import PriceRequest, DataDisk

req = PriceRequest(
    region_uuid="...",
    flavor_uuid="...",
    image_uuid="...",
    system_disk=40,
    billing_model=2,     # 1=monthly, 2=hourly
    service_period=1,
    data_disk=[DataDisk(name="data", disk_size=100, disk_type=1)],
)
result = client.planet.get_price(req)
print(f"$/hour: {result.total_price}")
print(f"$/month (approx): {result.total_price * 24 * 30:.2f}")
```

### Create an Instance

```python
from ows.models import CreateRequest

req = CreateRequest(
    region_uuid="...",
    flavor_uuid="...",
    image_uuid="...",
    system_disk=40,
    billing_model=2,
    service_period=1,
    name="my-server",
    adminPass="MyP@ssw0rd!",
    remark="test instance",
)
result = client.planet.create(req)
print(result.uuid)   # may be empty — creation is async
```

### List & Inspect Instances

```python
from ows.models import ListRequest

# List
result = client.planet.list_instances(ListRequest(page_num=1, page_size=50))
for inst in result.list:
    print(f"{inst.name:20s}  {inst.public_ip:15s}  {inst.status_name}")

# Detail
detail = client.planet.get_detail("instance-uuid")
print(f"Name: {detail.name}, Status: {detail.status_name}")
print(f"IP: {detail.public_port.get('ip', '')}, Port: {detail.public_port.get('port', '')}")
```

### Power Management

```python
client.planet.start("instance-uuid")
client.planet.stop("instance-uuid")
client.planet.reboot("instance-uuid", reboot_type=0)  # 0=soft, 1=hard
```

### Destroy an Instance

```python
client.product.free("instance-uuid")
```

### Check Status

```python
result = client.product.get_status("instance-uuid")
print(f"Status: {result.status}")  # 0=del, 1=running, 3=suspend, 4=down, 16=creating
```

### Billing

```python
from ows.models import OrderListRequest, BillMonthRequest

# Billing records
orders = client.order.list_orders(OrderListRequest(status=1, page_num=1, page_size=20))
for o in orders.list:
    print(f"  {o.order_sn}  ${o.amount}  {o.ctime}")

# Monthly bill
bill = client.bill.get_detail_by_month(BillMonthRequest(
    begin_date="1775001600",  # Unix timestamps
    end_date="1777593599",
    team_uuid="...",
))
print(f"Total: {bill.user_total_money} USD")
for item in bill.list:
    print(f"  {item.name} ({item.ip}) [{item.region_name}]: {item.total_money} USD")
```

### Error Handling

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

## License

MIT — see [LICENSE](LICENSE).
