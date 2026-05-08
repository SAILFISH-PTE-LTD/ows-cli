"""Resolve readable identifiers (name/type/code) → UUIDs."""
import click
from ows.models import ListRequest

# --- Fixed type → name mappings ---

CATEGORY_TYPES = {
    0: "Shared vCPU",
    1: "Dedicated vCPU",
    2: "Bare Metal",
}
CATEGORY_DEFAULT = 0

FLAVOR_TYPES = {
    0: "1C-2G",    1: "2C-4G",    2: "2C-8G",
    3: "4C-8G",    4: "4C-16G",   5: "8C-16G",
    6: "8C-32G",   7: "16C-32G",  8: "16C-64G",
}
FLAVOR_DEFAULT = 0

IMAGE_TYPES = {
    0:  "Ubuntu 20.04",          1:  "Ubuntu 18.04",
    2:  "Ubuntu 22.04",          3:  "Ubuntu 24.04",
    4:  "Debian 10",             5:  "Debian 11",
    6:  "Debian 12",             7:  "Debian 13",
    8:  "CentOS 7.3",            9:  "CentOS 7.5",
    10: "CentOS 7.6",           11: "CentOS 7.9",
    12: "CentOS 8 Stream",      13: "CentOS 9 Stream",
    14: "Rocky 9",              15: "Rocky 10",
    16: "AlmaLinux OS 9",       17: "AlmaLinux OS 10",
    18: "Windows 10 Pro",       19: "Windows 2012 R2 Standard",
    20: "Windows 2016 Standard", 21: "Windows 2019 Standard",
}
IMAGE_DEFAULT = 0

# Reverse mappings: name → type
CATEGORY_NAME_TO_TYPE = {v: k for k, v in CATEGORY_TYPES.items()}
FLAVOR_NAME_TO_TYPE = {v: k for k, v in FLAVOR_TYPES.items()}
IMAGE_NAME_TO_TYPE = {v: k for k, v in IMAGE_TYPES.items()}


def _type_error(label, mapping, value):
    items = [f"{k}={v}" for k, v in list(mapping.items())[:10]]
    click.echo(f"Error: unknown {label} '{value}'", err=True)
    click.echo(f"Available: {', '.join(items)}", err=True)
    raise click.Abort()


def resolve_region(client, value: str) -> str:
    """city_code or name → region_uuid. Falls back to treating value as UUID."""
    if not value:
        return ""
    regions = client.product.get_region()
    val_lower = value.lower().strip()
    # Exact match on city_code
    for r in regions:
        for child in r.children:
            for z in child.get("zone", []):
                if z.get("city_code", "").lower() == val_lower:
                    return z["region_uuid"]
    # Substring match on name
    for r in regions:
        for child in r.children:
            for z in child.get("zone", []):
                if val_lower in child.get("name", "").lower():
                    return z["region_uuid"]
    # Fallback: treat as UUID
    return value


def resolve_category(client, value: str) -> str:
    """type(0/1/2) or name → category_uuid."""
    if not value:
        return ""
    try:
        t = int(value)
        name = CATEGORY_TYPES.get(t)
        if not name:
            _type_error("category type", CATEGORY_TYPES, value)
    except ValueError:
        name = value.strip()
    types = client.planet.get_planet_type()
    for t in types:
        if t.name.lower() == name.lower():
            return t.category_uuid
    _type_error("category type", CATEGORY_TYPES, value)


def resolve_flavor(client, region_uuid: str, category_uuid: str, value: str) -> str:
    """type(0-8) or name → flavor_uuid."""
    if not value:
        return ""
    try:
        t = int(value)
        name = FLAVOR_TYPES.get(t)
        if not name:
            _type_error("flavor type", FLAVOR_TYPES, value)
    except ValueError:
        name = value.strip()
    flavors = client.planet.get_flavor_by_add(region_uuid, category_uuid)
    for f in flavors:
        if f.name.lower() == name.lower():
            return f.uuid
    _type_error("flavor type", FLAVOR_TYPES, value)


def resolve_image(client, region_uuid: str, value: str) -> str:
    """type(0-21) or name → image_uuid."""
    if not value:
        return ""
    try:
        t = int(value)
        name = IMAGE_TYPES.get(t)
        if not name:
            _type_error("image type", IMAGE_TYPES, value)
    except ValueError:
        name = value.strip()
    images = client.planet.get_image_by_region(region_uuid)
    for group in images:
        for img in group.images:
            if img.get("name", "").lower() == name.lower():
                return img.get("uuid", "")
    # Try name as UUID directly
    return value


def resolve_instance(client, value: str):
    """name/IP/UUID → Instance. Returns Instance object or None."""
    if not value:
        return None
    v = value.strip()

    # Looks like an IP? Do client-side exact match to avoid fuzzy API behavior
    if _looks_like_ip(v):
        result = client.planet.list_instances(ListRequest(page_num=1, page_size=200))
        for inst in result.list:
            if inst.public_ip == v:
                return inst
        return None

    # Looks like a UUID? Verify directly
    if _looks_like_uuid(v):
        try:
            return client.planet.get_detail(v)
        except Exception:
            return None

    # Otherwise treat as name — exact match via API
    result = client.planet.list_instances(ListRequest(name=v, page_size=1))
    if result.list:
        return result.list[0]
    # Partial name match
    result = client.planet.list_instances(ListRequest(keyword=v, page_size=1))
    if result.list:
        return result.list[0]
    return None


def _looks_like_ip(value: str) -> bool:
    return "." in value and len(value) <= 21 and all(p.isdigit() for p in value.split(".") if p)


def _looks_like_uuid(value: str) -> bool:
    return "-" in value and len(value) >= 32


def resolve_project(client, value: str = "") -> str:
    """name → project_uuid. Default to 'metro' if empty."""
    projects = client.post("/console/userProject/getList", {})
    if isinstance(projects, dict):
        projects = projects.get("list", projects.get("data", []))
    if not value:
        value = "metro"
    val_lower = value.lower().strip()
    for p in (projects or []):
        if p.get("name", "").lower() == val_lower:
            return p["uuid"]
    return value if isinstance(projects, list) and any(p.get("uuid") == value for p in projects) else ""
