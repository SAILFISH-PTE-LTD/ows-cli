"""Product commands."""
import click

from ows.cli import _hint, _show_error, handle_api_errors, pass_client, STATUS_MAP, json_output


@click.group()
def product():
    """Manage product resources."""
    pass


@product.command("free")
@click.argument("uuid", required=False, metavar="INSTANCE_UUID")
@click.option("--ip", default="", help="Free instance by public IP instead of UUID")
@handle_api_errors
@pass_client
def product_free(client, uuid, ip):
    """Destroy (free) a resource by UUID or IP."""
    if ip:
        from ows.models import ListRequest
        result = client.planet.list_instances(ListRequest(page_num=1, page_size=200))
        for inst in result.list:
            if inst.public_ip == ip:
                uuid = inst.uuid
                break
        if not uuid:
            _show_error(f"No instance found with IP {ip}", "ows product free --ip <IP>")
    if not uuid:
        _show_error("Missing INSTANCE_UUID or --ip", "ows product free <INSTANCE_UUID>  or  ows product free --ip <IP>", _hint("instance"))
    client.product.free(uuid)
    if json_output({"ok": True, "action": "free", "uuid": uuid}):
        return
    click.echo(f"Destroyed: {uuid}")


@product.command("status")
@click.argument("uuid", required=False, metavar="INSTANCE_UUID")
@handle_api_errors
@pass_client
def product_status(client, uuid):
    """Check resource status."""
    if not uuid:
        _show_error("Missing INSTANCE_UUID", "ows product status <INSTANCE_UUID>", _hint("instance"))
    result = client.product.get_status(uuid)
    name = STATUS_MAP.get(result.status)
    if json_output({"uuid": uuid, "status": result.status, "status_name": name}):
        return
    status_str = f"{result.status} ({name})" if name else str(result.status)
    click.echo(f"UUID: {uuid}")
    click.echo(f"Status: {status_str}")


@product.command("regions")
@click.option("--category", default="", help="Category UUID (optional)")
@handle_api_errors
@pass_client
def product_regions(client, category):
    """List available regions."""
    result = client.product.get_region(category)
    zones = []
    for r in result:
        for child in r.children:
            for z in child.get("zone", []):
                zones.append({
                    "region": r.name,
                    "name": child.get("name", ""),
                    "city_code": z.get("city_code", ""),
                    "region_uuid": z.get("region_uuid", ""),
                })
    if json_output(zones):
        return
    click.echo(f"{'Region':30s}  {'City Code':8s}  {'Region UUID'}")
    click.echo("-" * 90)
    for r in result:
        click.echo(f"{r.name:30s}")
        for child in r.children:
            for z in child.get("zone", []):
                click.echo(f"  {child.get('name', ''):28s}  {z.get('city_code', ''):8s}  {z.get('region_uuid', '')}")
