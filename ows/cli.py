"""ows.us VPS management CLI."""
import functools
import json
import sys
import click
from ows.client import OwsClient
from ows.errors import OwsError
from ows.models import (
    PriceRequest, CreateRequest, ListRequest, DataDisk,
)


pass_client = click.make_pass_decorator(OwsClient)


def handle_api_errors(func):
    """Decorator to catch OwsError in all CLI commands."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except OwsError as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)
    return wrapper


UUID_HELP = {
    "instance": "Use: ows planet list",
    "region": "Use: ows product regions",
    "category": "Use: ows planet types",
    "image": "Use: ows planet images --region <REGION_UUID>",
    "flavor": "Use: ows planet flavors --region <REGION_UUID> --category <CATEGORY_UUID>",
}

STATUS_MAP = {
    # From API docs: https://api.ows.us/apidoc/index.html#/md?appKey=console&key=docs%252FResourceStatus
    0: "Deleted",
    1: "Running",
    3: "Suspend",
    4: "Down",
    16: "Creating",
    106: "Executing",
}


@click.group()
@click.option("-c", "--config", default="config.json", help="Config file path")
@click.pass_context
def cli(ctx, config):
    """ows — manage VPS resources via ows.us API."""
    try:
        ctx.obj = OwsClient.from_config(config)
    except (OwsError, FileNotFoundError, KeyError) as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


# --- planet ---

@cli.group()
def planet():
    """Manage Planet (VPS) instances."""
    pass


@planet.command("types")
@handle_api_errors
@pass_client
def planet_types(client):
    """List product categories."""
    result = client.planet.get_planet_type()
    click.echo(f"{'Category UUID':36s}  {'Name':20s}  Status  Billing")
    click.echo("-" * 80)
    for t in result:
        click.echo(f"{t.category_uuid}  {t.name:20s}  {t.status:6d}  {t.billing_model}")


@planet.command("images")
@click.option("--region", required=False, help="Region UUID")
@click.option("--self", "is_self", default=0, help="Self-owned images (1=yes)")
@handle_api_errors
@pass_client
def planet_images(client, region, is_self):
    """List available images in a region."""
    if not region:
        click.echo(f"Error: Missing --region UUID. {UUID_HELP['region']}", err=True)
        sys.exit(1)
    result = client.planet.get_image_by_region(region, is_self)
    for group in result:
        click.echo(f"\n{group.name} ({group.icon_type})")
        click.echo(f"  {'ID':5s}  {'Name':35s}  UUID")
        click.echo(f"  {'-'*5}  {'-'*35}  {'-'*36}")
        for img in group.images:
            click.echo(f"  {img['id']:5d}  {img['name']:35s}  {img.get('uuid', '')}")


@planet.command("flavors")
@click.option("--region", required=False, help="Region UUID")
@click.option("--category", required=False, help="Category UUID")
@handle_api_errors
@pass_client
def planet_flavors(client, region, category):
    """List available flavors."""
    if not region:
        click.echo(f"Error: Missing --region UUID. {UUID_HELP['region']}", err=True)
        sys.exit(1)
    if not category:
        click.echo(f"Error: Missing --category UUID. {UUID_HELP['category']}", err=True)
        sys.exit(1)
    result = client.planet.get_flavor_by_add(region, category)
    click.echo(f"{'Name':20s}  {'UUID':36s}  Cores  Memory  Price/h     Price/m")
    click.echo("-" * 100)
    for f in result:
        cores = str(f.cores).rjust(4)
        mem = str(f.memory).rjust(6)
        click.echo(f"{f.name:20s}  {f.uuid}  {cores}  {mem}  ${float(str(f.h_price)):<10.8f}  ${float(str(f.m_price)):<10.2f}")


@planet.command("price")
@click.option("--region", required=False, help="Region UUID")
@click.option("--flavor", required=False, help="Flavor UUID")
@click.option("--image", required=False, help="Image UUID")
@click.option("--system-disk", type=int, required=False)
@click.option("--billing-model", type=int, required=False, help="1=subscription, 2=pay-as-you-go")
@click.option("--service-period", type=int, required=False)
@click.option("--coupon-id", type=int, default=0)
@click.option("--user-time", type=int, default=0)
@click.option("--data-disk-json", default="[]", help='JSON array of {name,disk_size,disk_type}')
@handle_api_errors
@pass_client
def planet_price(client, region, flavor, image, system_disk, billing_model, service_period,
                 coupon_id, user_time, data_disk_json):
    """Calculate configuration price."""
    if not region:
        click.echo(f"Error: Missing --region UUID. {UUID_HELP['region']}", err=True)
        sys.exit(1)
    if not flavor:
        click.echo(f"Error: Missing --flavor UUID. {UUID_HELP['flavor']}", err=True)
        sys.exit(1)
    if not image:
        click.echo(f"Error: Missing --image UUID. {UUID_HELP['image']}", err=True)
        sys.exit(1)
    if system_disk is None:
        click.echo("Error: Missing --system-disk <GB>", err=True)
        sys.exit(1)
    if billing_model is None:
        click.echo("Error: Missing --billing-model (1=subscription, 2=pay-as-you-go)", err=True)
        sys.exit(1)
    if service_period is None:
        click.echo("Error: Missing --service-period <N>", err=True)
        sys.exit(1)
    disks = [DataDisk(**d) for d in json.loads(data_disk_json)]
    req = PriceRequest(
        region_uuid=region, flavor_uuid=flavor, image_uuid=image,
        system_disk=system_disk, billing_model=billing_model, service_period=service_period,
        coupon_id=coupon_id, user_time=user_time, data_disk=disks,
    )
    result = client.planet.get_price(req)
    click.echo(f"Total: ${result.total_price} (original: ${result.original_price}, discount: ${result.discount_price})")


@planet.command("create")
@click.option("--region", required=False, help="Region UUID")
@click.option("--flavor", required=False, help="Flavor UUID")
@click.option("--image", required=False, help="Image UUID")
@click.option("--system-disk", type=int, required=False)
@click.option("--billing-model", type=int, required=False, help="1=subscription, 2=pay-as-you-go")
@click.option("--service-period", type=int, required=False)
@click.option("--project", default="")
@click.option("--admin-pass", default="")
@click.option("--ssh-key", default="")
@click.option("--remark", default="")
@click.option("--is-renew", type=int, default=0)
@click.option("--is-backup", type=int, default=0)
@click.option("--data-disk-json", default="[]")
@handle_api_errors
@pass_client
def planet_create(client, region, flavor, image, system_disk, billing_model, service_period,
                  project, admin_pass, ssh_key, remark, is_renew, is_backup, data_disk_json):
    """Create a new Planet instance."""
    if not region:
        click.echo(f"Error: Missing --region UUID. {UUID_HELP['region']}", err=True)
        sys.exit(1)
    if not flavor:
        click.echo(f"Error: Missing --flavor UUID. {UUID_HELP['flavor']}", err=True)
        sys.exit(1)
    if not image:
        click.echo(f"Error: Missing --image UUID. {UUID_HELP['image']}", err=True)
        sys.exit(1)
    if system_disk is None:
        click.echo("Error: Missing --system-disk <GB>", err=True)
        sys.exit(1)
    if billing_model is None:
        click.echo("Error: Missing --billing-model (1=subscription, 2=pay-as-you-go)", err=True)
        sys.exit(1)
    if service_period is None:
        click.echo("Error: Missing --service-period <N>", err=True)
        sys.exit(1)
    disks = [DataDisk(**d) for d in json.loads(data_disk_json)]
    req = CreateRequest(
        region_uuid=region, flavor_uuid=flavor, image_uuid=image,
        system_disk=system_disk, billing_model=billing_model, service_period=service_period,
        project_uuid=project, adminPass=admin_pass, ssh_key=ssh_key,
        remark=remark, is_renew=is_renew, is_backup=is_backup, data_disk=disks,
    )
    result = client.planet.create(req)
    click.echo(f"Created: {result.uuid}")


@planet.command("list")
@click.option("--region", default="", help="Filter by region UUID (from: ows product regions)")
@click.option("--page", type=int, default=1)
@click.option("--size", type=int, default=20)
@click.option("--name", default="")
@click.option("--ip", default="")
@click.option("--status", default="")
@handle_api_errors
@pass_client
def planet_list(client, region, page, size, name, ip, status):
    """List Planet instances."""
    req = ListRequest(
        page_num=page, page_size=size, region_uuid=region,
        name=name, ip=ip, status=status,
    )
    result = client.planet.list_instances(req)
    header = f"{'UUID':36s}  {'Name':20s}  {'Status':8s}  {'Public IP':15s}  {'Flavor':10s}  {'Region UUID'}"
    click.echo(header)
    click.echo("-" * len(header))
    for inst in result.list:
        click.echo(f"{inst.uuid:36s}  {inst.name:20s}  {inst.status_name:8s}  {inst.public_ip:15s}  {inst.flavor_name:10s}  {inst.region_uuid}")
    click.echo(f"--- {result.total} total")


@planet.command("detail")
@click.argument("uuid", required=False, metavar="INSTANCE_UUID")
@click.option("--project", default=None)
@handle_api_errors
@pass_client
def planet_detail(client, uuid, project):
    """Show instance detail."""
    if not uuid:
        click.echo(f"Error: Missing INSTANCE_UUID. {UUID_HELP['instance']}", err=True)
        sys.exit(1)
    inst = client.planet.get_detail(uuid, project)
    fields = [
        ("UUID", inst.uuid), ("Name", inst.name), ("Status", f"{inst.status_name} ({inst.status})"),
        ("Region", f"{inst.city_name} ({inst.region_uuid})"),
        ("Flavor", inst.flavor_name), ("Cores", inst.cores), ("Memory", inst.memory),
        ("Storage", inst.storage), ("GPU", inst.gpu or "none"),
        ("Created", inst.create_time), ("Expires", inst.end_time),
        ("Image", inst.image_uuid), ("Project", inst.project_uuid),
        ("Ports", f"private={inst.private_port}, public={inst.public_port}"),
    ]
    for label, value in fields:
        click.echo(f"{label:12s}: {value}")


@planet.command("stop")
@click.argument("uuid", required=False, metavar="INSTANCE_UUID")
@handle_api_errors
@pass_client
def planet_stop(client, uuid):
    """Stop an instance."""
    if not uuid:
        click.echo(f"Error: Missing INSTANCE_UUID. {UUID_HELP['instance']}", err=True)
        sys.exit(1)
    client.planet.stop(uuid)


@planet.command("start")
@click.argument("uuid", required=False, metavar="INSTANCE_UUID")
@handle_api_errors
@pass_client
def planet_start(client, uuid):
    """Start an instance."""
    if not uuid:
        click.echo(f"Error: Missing INSTANCE_UUID. {UUID_HELP['instance']}", err=True)
        sys.exit(1)
    client.planet.start(uuid)


@planet.command("reboot")
@click.argument("uuid", required=False, metavar="INSTANCE_UUID")
@click.argument("reboot_type", type=int, required=False)
@handle_api_errors
@pass_client
def planet_reboot(client, uuid, reboot_type):
    """Reboot an instance."""
    if not uuid:
        click.echo(f"Error: Missing INSTANCE_UUID. {UUID_HELP['instance']}", err=True)
        sys.exit(1)
    if reboot_type is None:
        click.echo("Error: Missing reboot_type argument.", err=True)
        sys.exit(1)
    client.planet.reboot(uuid, reboot_type)
    click.echo(f"Rebooting: {uuid}")


# --- product ---

@cli.group()
def product():
    """Manage product resources."""
    pass


@product.command("free")
@click.argument("uuid", required=False, metavar="INSTANCE_UUID")
@handle_api_errors
@pass_client
def product_free(client, uuid):
    """Destroy (free) a resource."""
    if not uuid:
        click.echo(f"Error: Missing INSTANCE_UUID. {UUID_HELP['instance']}", err=True)
        sys.exit(1)
    client.product.free(uuid)


@product.command("status")
@click.argument("uuid", required=False, metavar="INSTANCE_UUID")
@handle_api_errors
@pass_client
def product_status(client, uuid):
    """Check resource status."""
    if not uuid:
        click.echo(f"Error: Missing INSTANCE_UUID. {UUID_HELP['instance']}", err=True)
        sys.exit(1)
    result = client.product.get_status(uuid)
    name = STATUS_MAP.get(result.status)
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
    click.echo(f"{'Region':30s}  {'City Code':8s}  {'Region UUID'}")
    click.echo("-" * 90)
    for r in result:
        click.echo(f"{r.name:30s}")
        for child in r.children:
            zones = child.get("zone", [])
            for z in zones:
                click.echo(f"  {child.get('name', ''):28s}  {z.get('city_code', ''):8s}  {z.get('region_uuid', '')}")


if __name__ == "__main__":
    cli()
