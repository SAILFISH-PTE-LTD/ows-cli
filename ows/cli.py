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
    for t in result:
        click.echo(f"{t.category_uuid}  {t.name:20s}  status={t.status}  billing={t.billing_model}")


@planet.command("images")
@click.option("--region", required=True, help="Region UUID")
@click.option("--self", "is_self", default=0, help="Self-owned images (1=yes)")
@handle_api_errors
@pass_client
def planet_images(client, region, is_self):
    """List available images in a region."""
    result = client.planet.get_image_by_region(region, is_self)
    for img in result:
        click.echo(f"{img.id:5d}  {img.name:30s}  {img.uuid}")


@planet.command("flavors")
@click.option("--region", required=True, help="Region UUID")
@click.option("--category", required=True, help="Category UUID")
@handle_api_errors
@pass_client
def planet_flavors(client, region, category):
    """List available flavors."""
    result = client.planet.get_flavor_by_add(region, category)
    for f in result:
        cores = f.cores.rjust(4)
        mem = f.memory.rjust(6)
        click.echo(f"{f.name:20s}  {f.uuid}  {cores} cores  {mem} mem  ${f.h_price}/h  ${f.m_price}/m")


@planet.command("price")
@click.option("--region", required=True)
@click.option("--flavor", required=True)
@click.option("--image", required=True)
@click.option("--system-disk", type=int, required=True)
@click.option("--billing-model", type=int, required=True)
@click.option("--service-period", type=int, required=True)
@click.option("--coupon-id", type=int, default=0)
@click.option("--user-time", type=int, default=0)
@click.option("--data-disk-json", default="[]", help='JSON array of {name,disk_size,disk_type}')
@handle_api_errors
@pass_client
def planet_price(client, region, flavor, image, system_disk, billing_model, service_period,
                 coupon_id, user_time, data_disk_json):
    """Calculate configuration price."""
    disks = [DataDisk(**d) for d in json.loads(data_disk_json)]
    req = PriceRequest(
        region_uuid=region, flavor_uuid=flavor, image_uuid=image,
        system_disk=system_disk, billing_model=billing_model, service_period=service_period,
        coupon_id=coupon_id, user_time=user_time, data_disk=disks,
    )
    result = client.planet.get_price(req)
    click.echo(f"Total: ${result.total_price} (original: ${result.original_price}, discount: ${result.discount_price})")


@planet.command("create")
@click.option("--region", required=True)
@click.option("--flavor", required=True)
@click.option("--image", required=True)
@click.option("--system-disk", type=int, required=True)
@click.option("--billing-model", type=int, required=True)
@click.option("--service-period", type=int, required=True)
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
@click.option("--region", default="")
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
    for inst in result.list:
        click.echo(f"{inst.uuid:36s}  {inst.name:20s}  {inst.status_name:8s}  {inst.public_ip:15s}  {inst.flavor_name}")
    click.echo(f"--- {result.total} total")


@planet.command("detail")
@click.argument("uuid")
@click.option("--project", default=None)
@handle_api_errors
@pass_client
def planet_detail(client, uuid, project):
    """Show instance detail."""
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
@click.argument("uuid")
@handle_api_errors
@pass_client
def planet_stop(client, uuid):
    """Stop an instance."""
    client.planet.stop(uuid)
    click.echo(f"Stopped: {uuid}")


@planet.command("start")
@click.argument("uuid")
@handle_api_errors
@pass_client
def planet_start(client, uuid):
    """Start an instance."""
    client.planet.start(uuid)
    click.echo(f"Started: {uuid}")


@planet.command("reboot")
@click.argument("uuid")
@click.argument("reboot_type", type=int)
@handle_api_errors
@pass_client
def planet_reboot(client, uuid, reboot_type):
    """Reboot an instance."""
    client.planet.reboot(uuid, reboot_type)
    click.echo(f"Rebooting: {uuid}")


# --- product ---

@cli.group()
def product():
    """Manage product resources."""
    pass


@product.command("free")
@click.argument("uuid")
@handle_api_errors
@pass_client
def product_free(client, uuid):
    """Destroy (free) a resource."""
    client.product.free(uuid)
    click.echo(f"Freed: {uuid}")


@product.command("status")
@click.argument("uuid")
@handle_api_errors
@pass_client
def product_status(client, uuid):
    """Check resource status."""
    result = client.product.get_status(uuid)
    click.echo(f"Status: {result.status}")


if __name__ == "__main__":
    cli()
