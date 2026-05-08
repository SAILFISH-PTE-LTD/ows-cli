"""Product commands."""
import click

from ows.cli import _hint, _show_error, handle_api_errors, pass_client, STATUS_MAP, json_output
from ows.cli.resolvers import resolve_instance


@click.group()
def product():
    """Manage product resources."""
    pass


@product.command("free")
@click.argument("instance", required=False, metavar="UUID|NAME|IP")
@handle_api_errors
@pass_client
def product_free(client, instance):
    """Destroy (free) a resource by UUID, name, or IP."""
    if not instance:
        _show_error("Missing UUID|NAME|IP", "ows product free <UUID|NAME|IP>", _hint("instance"))
    inst = resolve_instance(client, instance)
    if not inst:
        _show_error(f"No instance found: {instance}", "ows product free <UUID|NAME|IP>")
    client.product.free(inst.uuid)
    if json_output({"ok": True, "action": "free", "uuid": inst.uuid}):
        return
    click.echo(f"Destroyed: {inst.uuid}")


@product.command("status")
@click.argument("instance", required=False, metavar="UUID|NAME|IP")
@handle_api_errors
@pass_client
def product_status(client, instance):
    """Check resource status by UUID, name, or IP."""
    if not instance:
        _show_error("Missing UUID|NAME|IP", "ows product status <UUID|NAME|IP>", _hint("instance"))
    inst = resolve_instance(client, instance)
    if not inst:
        _show_error(f"No instance found: {instance}", "ows product status <UUID|NAME|IP>")
    result = client.product.get_status(inst.uuid)
    name = STATUS_MAP.get(result.status)
    if json_output({"uuid": inst.uuid, "status": result.status, "status_name": name}):
        return
    status_str = f"{result.status} ({name})" if name else str(result.status)
    click.echo(f"UUID: {inst.uuid}")
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
