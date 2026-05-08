"""Planet (VPS) commands."""
import json
import random
import string
import time

import click

from ows.cli import _hint, _show_error, handle_api_errors, pass_client, json_output
from ows.errors import APIError
import sys

from ows.deploy import DeployClient, REGION_MAP
from ows.models import CreateRequest, DataDisk, DeployRequest, ListRequest, PriceRequest, VpsLoginInfo


_DEFAULT_FLAVOR_CORES = 1
_DEFAULT_FLAVOR_MEM = 2
_DEFAULT_IMAGE_KW = "ubuntu 20"


def _gen_password(length=16):
    special = "!@#$%^&*"
    chars = [
        random.choice(string.ascii_uppercase),
        random.choice(string.ascii_lowercase),
        random.choice(string.digits),
        random.choice(special),
    ]
    all_chars = string.ascii_letters + string.digits + special
    chars += [random.choice(all_chars) for _ in range(length - 4)]
    random.shuffle(chars)
    return "".join(chars)


def _safe_call(client, fn, *args, max_retries=3, **kwargs):
    for i in range(max_retries):
        try:
            return fn(*args, **kwargs)
        except APIError as e:
            msg = str(e).lower()
            if "too many requests" in msg or "too frequent" in msg:
                wait = 2 ** i
                click.echo(f"[retry] 限流，等待 {wait}s…", err=True)
                time.sleep(wait)
                continue
            raise
    raise APIError(400, "rate limit retries exhausted", {})


def _get_city_code(client, region_uuid):
    regions = client.product.get_region()
    for r in regions:
        for child in r.children:
            for z in child.get("zone", []):
                if z.get("region_uuid") == region_uuid:
                    return z.get("city_code", "")
    return ""


def _resolve_defaults(client, region_uuid, flavor, image, project):
    if not flavor:
        types = _safe_call(client, client.planet.get_planet_type)
        shared = next((t for t in types if "Shared" in t.name and "vCPU" in t.name), None)
        time.sleep(1)
        flavors = _safe_call(client, client.planet.get_flavor_by_add,
                             region_uuid, shared.category_uuid)
        f = next((x for x in flavors
                  if x.cores == _DEFAULT_FLAVOR_CORES and x.memory == _DEFAULT_FLAVOR_MEM), None)
        if f:
            flavor = f.uuid
            click.echo(f"[default] flavor: {f.name} → {flavor}")
        time.sleep(1)
    if not image:
        images = _safe_call(client, client.planet.get_image_by_region, region_uuid)
        for group in images:
            for img in group.images:
                if _DEFAULT_IMAGE_KW in img.get("name", "").lower():
                    image = img["uuid"]
                    click.echo(f"[default] image: {img['name']} → {image}")
                    break
            if image:
                break
        time.sleep(1)
    if not project:
        projects = _safe_call(client, client.post, "/console/userProject/getList", {})
        if isinstance(projects, dict):
            projects = projects.get("list", projects.get("data", []))
        p = next((x for x in projects if x.get("name", "").lower() == "metro"), None)
        if p:
            project = p["uuid"]
            click.echo(f"[default] project: metro → {project}")
        time.sleep(1)
    return flavor, image, project


def _poll_instance(client, name, region_uuid, timeout=120, interval=5):
    """Poll list_instances until the instance is Running."""
    start = time.monotonic()
    found = False
    while time.monotonic() - start < timeout:
        time.sleep(interval)
        result = _safe_call(client, client.planet.list_instances,
                            ListRequest(page_num=1, page_size=100, region_uuid=region_uuid))
        for inst in result.list:
            if inst.name == name:
                found = True
                if inst.status_name.lower() not in ("creating", "executing"):
                    return inst
                click.echo(f"\rStatus: {inst.status_name} (waiting for Running)...", nl=False)
                break
        if not found:
            click.echo(".", nl=False)
    return None


def _resolve_region_id(city_name):
    """Map ows.us city_name to deploy region_id."""
    if not city_name:
        click.echo("Error: city_name is empty, please provide --region-id manually", err=True)
        keys = list(REGION_MAP.keys())[:10]
        click.echo(f"Available region ids (first 10): {', '.join(keys)}", err=True)
        raise click.Abort()
    region_id = REGION_MAP.get(city_name)
    if not region_id:
        click.echo(f"Error: unknown city '{city_name}', please provide --region-id manually", err=True)
        keys = list(REGION_MAP.keys())[:10]
        click.echo(f"Available region ids (first 10): {', '.join(keys)}", err=True)
        raise click.Abort()
    return region_id


def _get_deploy_client(client, sos_token_arg):
    """Get or create DeployClient from config or CLI arg."""
    sos_token = sos_token_arg or (client.auth.config.sos_token if hasattr(client.auth, 'config') else "")
    if not sos_token:
        _show_error(
            "sos_token is required for deploy. Set it in config.json or use --sos-token",
            "ows planet deploy <UUID> --password PWD [--sos-token TOKEN]",
            "Get sos_token from dashboard.metrovpn.xyz cookie"
        )
    return DeployClient(sos_token)


def _build_vps_infos_from_detail(inst, password):
    """Build VpsLoginInfo list from InstanceDetail or Instance."""
    return [
        VpsLoginInfo(
            vps_id=inst.uuid,
            ip=inst.public_ip,
            password=password,
            os="ubuntu 20.04",
            vps_type="1C-2G",
            user="root",
            port="22",
        )
    ]


def _coerce_int(val, label):
    """Safely convert to int with error message."""
    try:
        return int(val)
    except (ValueError, TypeError):
        click.echo(f"Error: cannot convert {label}='{val}' to int", err=True)
        raise click.Abort()


@click.group()
def planet():
    """Manage Planet (VPS) instances."""
    pass


@planet.command("types")
@handle_api_errors
@pass_client
def planet_types(client):
    """List product categories."""
    result = client.planet.get_planet_type()
    if json_output([{"category_uuid": t.category_uuid, "name": t.name, "status": t.status,
                      "billing_model": t.billing_model} for t in result]):
        return
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
        _show_error("Missing --region UUID", "ows planet images --region <REGION_UUID>", _hint("region"))
    result = client.planet.get_image_by_region(region, is_self)
    if json_output([{"name": g.name, "icon_type": g.icon_type,
                      "images": g.images} for g in result]):
        return
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
        _show_error("Missing --region UUID",
                    "ows planet flavors --region <REGION_UUID> --category <CATEGORY_UUID>",
                    _hint("region", "category"))
    if not category:
        _show_error("Missing --category UUID",
                    "ows planet flavors --region <REGION_UUID> --category <CATEGORY_UUID>",
                    _hint("region", "category"))
    result = client.planet.get_flavor_by_add(region, category)
    if json_output([{"uuid": f.uuid, "name": f.name, "cores": f.cores, "memory": f.memory,
                      "h_price": float(str(f.h_price)), "m_price": float(str(f.m_price))}
                     for f in result]):
        return
    click.echo(f"{'Name':20s}  {'UUID':36s}  Cores  Memory  Price/h     Price/m")
    click.echo("-" * 100)
    for f in result:
        cores = str(f.cores).rjust(4)
        mem = str(f.memory).rjust(6)
        click.echo(f"{f.name:20s}  {f.uuid}  {cores}  {mem}  "
                   f"${float(str(f.h_price)):<10.8f}  ${float(str(f.m_price)):<10.2f}")


@planet.command("price")
@click.option("--region", required=False, help="Region UUID")
@click.option("--flavor", required=False, help="Flavor UUID")
@click.option("--image", required=False, help="Image UUID")
@click.option("--system-disk", type=int, default=40, help="System disk size in GB")
@click.option("--billing-model", type=int, default=2, help="1=subscription, 2=pay-as-you-go")
@click.option("--service-period", type=int, default=1,
              help="Service period (months for subscription, 1 for hourly)")
@click.option("--coupon-id", type=int, default=0)
@click.option("--user-time", type=int, default=0)
@click.option("--data-disk-json", default="[]", help='JSON array of {name,disk_size,disk_type}')
@handle_api_errors
@pass_client
def planet_price(client, region, flavor, image, system_disk, billing_model, service_period,
                 coupon_id, user_time, data_disk_json):
    """Calculate configuration price."""
    if not region:
        _show_error("Missing --region UUID",
                    "ows planet price --region <REGION_UUID>",
                    _hint("region"))
    flavor, image, _project = _resolve_defaults(client, region, flavor, image, "")
    if not flavor:
        _show_error("Missing --flavor UUID",
                    "ows planet price --region <REGION_UUID> --flavor <FLAVOR_UUID>",
                    _hint("region", "flavor", "image"))
    if not image:
        _show_error("Missing --image UUID",
                    "ows planet price ... --image <IMAGE_UUID>",
                    _hint("region", "flavor", "image"))
    disks = [DataDisk(**d) for d in json.loads(data_disk_json)]
    req = PriceRequest(
        region_uuid=region, flavor_uuid=flavor, image_uuid=image,
        system_disk=system_disk, billing_model=billing_model, service_period=service_period,
        coupon_id=coupon_id, user_time=user_time, data_disk=disks,
    )
    result = client.planet.get_price(req)
    data = {
        "flavor_price": result.flavor_price, "image_price": result.image_price,
        "system_disk_price": result.system_disk_price, "data_disk_price": result.data_disk_price,
        "ip_price": result.ip_price, "flow_price": result.flow_price,
        "total_price": result.total_price, "original_price": result.original_price,
        "discount_price": result.discount_price, "coupon_price": result.coupon_price,
    }
    if billing_model == 2:
        data["monthly_approx"] = round(result.total_price * 24 * 30, 2)
        data["unit"] = "hour"
    else:
        data["unit"] = "month"
    if json_output(data):
        return
    unit = "/月" if billing_model == 1 else "/小时"
    click.echo(f"价格明细 ({unit}):")
    click.echo(f"  规格 (CPU+内存):      ${result.flavor_price:.8f}  /实例{unit}")
    click.echo(f"  镜像:                 ${result.image_price:.8f}  /实例{unit}")
    sd_per_gb = result.system_disk_price / system_disk if system_disk else 0
    click.echo(f"  系统盘 ({system_disk}GB):      ${result.system_disk_price:.8f}  "
               f"(≈ ${sd_per_gb:.8f}/GB{unit})")
    if result.data_disk_price:
        click.echo(f"  数据盘:               ${result.data_disk_price:.8f}  /总计{unit}")
    click.echo(f"  IP:                   ${result.ip_price:.8f}  /IP{unit}")
    click.echo(f"  流量:                 ${result.flow_price:.8f}  /总计{unit}")
    click.echo("-" * 60)
    click.echo(f"  原价:                 ${result.original_price:.8f}")
    if result.discount_price:
        click.echo(f"  折扣:                -${result.discount_price:.8f}")
    if result.coupon_price:
        click.echo(f"  优惠券:              -${result.coupon_price:.8f}")
    click.echo(f"  合计:                 ${result.total_price:.8f}  {unit}")
    if billing_model == 2:
        monthly = result.total_price * 24 * 30
        click.echo(f"  ≈ 折合月费:           ${monthly:.2f}")


@planet.command("create")
@click.option("--region", required=False, help="Region UUID")
@click.option("--flavor", required=False, help="Flavor UUID")
@click.option("--image", required=False, help="Image UUID")
@click.option("--system-disk", type=int, default=40, help="System disk size in GB")
@click.option("--billing-model", type=int, default=2, help="1=subscription, 2=pay-as-you-go")
@click.option("--service-period", type=int, default=1,
              help="Service period (months for subscription, 1 for hourly)")
@click.option("--project", default="")
@click.option("--name", default="", help="Instance name (auto-generated: Planet-{city}-{random})")
@click.option("--admin-pass", default="", help="Admin password (auto-generated if not set)")
@click.option("--ssh-key", default="")
@click.option("--remark", default="")
@click.option("--is-renew", type=int, default=0)
@click.option("--is-backup", type=int, default=0)
@click.option("--data-disk-json", default="[]")
@click.option("--no-wait", is_flag=True, help="Don't wait for provisioning, return immediately")
@click.option("--deploy", is_flag=True, help="Deploy to MetroVPN after creation")
@click.option("--sos-token", default="", help="sos_token for deploy")
@click.option("--deploy-region-id", default="", help="Override auto-detected region_id")
@click.option("--deploy-os", default="ubuntu 20.04")
@click.option("--deploy-type", default="1C-2G")
@click.option("--deploy-user", default="root")
@click.option("--deploy-port", default="22")
@click.option("--deploy-quota-type", type=int, default=0)
@click.option("--deploy-quota", type=int, default=2000)
@click.option("--deploy-bandwidth", type=int, default=100)
@click.option("--deploy-group-id", default="Vip HighSpeed Server")
@handle_api_errors
@pass_client
def planet_create(client, region, flavor, image, system_disk, billing_model, service_period,
                  project, name, admin_pass, ssh_key, remark, is_renew, is_backup,
                  data_disk_json, no_wait,
                  deploy, sos_token, deploy_region_id, deploy_os, deploy_type, deploy_user, deploy_port,
                  deploy_quota_type, deploy_quota, deploy_bandwidth, deploy_group_id):
    """Create a new Planet instance."""
    if not region:
        _show_error("Missing --region UUID",
                    "ows planet create --region <REGION_UUID>",
                    _hint("region"))
    flavor, image, project = _resolve_defaults(client, region, flavor, image, project)
    if not flavor:
        _show_error("Missing --flavor UUID",
                    "ows planet create --region <REGION_UUID> --flavor <FLAVOR_UUID>",
                    _hint("region", "flavor", "image"))
    if not image:
        _show_error("Missing --image UUID",
                    "ows planet create ... --image <IMAGE_UUID>",
                    _hint("region", "flavor", "image"))

    if not name:
        city_code = _get_city_code(client, region)
        suffix = "".join(random.choices(string.ascii_letters + string.digits, k=6))
        name = f"Planet-{city_code}-{suffix}"
        click.echo(f"[default] name: {name}")

    disks = [DataDisk(**d) for d in json.loads(data_disk_json)]
    if not admin_pass:
        admin_pass = _gen_password()

    req = CreateRequest(
        region_uuid=region, flavor_uuid=flavor, image_uuid=image,
        system_disk=system_disk, billing_model=billing_model, service_period=service_period,
        project_uuid=project, adminPass=admin_pass, ssh_key=ssh_key,
        name=name, remark=remark, is_renew=is_renew, is_backup=is_backup,
        data_disk=disks,
    )
    result = client.planet.create(req)
    if result.uuid:
        if json_output({"uuid": result.uuid, "name": name, "password": admin_pass}):
            return
        click.echo(f"Created: {result.uuid}")
        click.echo(f"Password: {admin_pass}")
        return

    if no_wait:
        if json_output({"uuid": None, "name": name, "password": admin_pass, "status": "provisioning"}):
            return
        click.echo("Sent, async creation in progress")
        click.echo(f"Password: {admin_pass}")
        click.echo(f"Check status: ows planet list --name \"{name}\"")
        return

    click.echo("Waiting for provisioning...", nl=False)
    inst = _poll_instance(client, name, region)
    click.echo()
    if inst:
        if json_output({"uuid": inst.uuid, "name": inst.name, "status": inst.status_name,
                        "public_ip": inst.public_ip, "password": admin_pass}):
            return
        click.echo(f"Created: {inst.uuid}")
        click.echo(f"Name:    {inst.name}")
        click.echo(f"Status:  {inst.status_name}")
        click.echo(f"Public IP: {inst.public_ip}")
        click.echo(f"Password: {admin_pass}")
        click.echo(f"Connect:  ssh root@{inst.public_ip}")
    else:
        if json_output({"error": "timeout", "name": name, "password": admin_pass}):
            return
        click.echo(f"Timeout — instance not found in list. Check later with:")
        click.echo(f"  ows planet list --name \"{name}\"")

    # --- Deploy after create ---
    if deploy:
        if inst is None:
            click.echo("Error: --deploy requires instance info but creation did not return it", err=True)
            click.echo("Retry manually with: ows planet deploy <UUID> --password PWD", err=True)
            sys.exit(1)

        if not inst.public_ip:
            click.echo("Error: --deploy requires public IP but instance has none", err=True)
            click.echo("Retry manually with: ows planet deploy <UUID> --password PWD", err=True)
            sys.exit(1)

        region_id = deploy_region_id
        if not region_id:
            try:
                region_id = _resolve_region_id(inst.city_name)
            except click.Abort:
                click.echo("Error: cannot resolve region_id for deploy. Provide --deploy-region-id", err=True)
                sys.exit(1)

        vps_infos = _build_vps_infos_from_detail(inst, admin_pass)
        vps_infos[0].os = deploy_os
        vps_infos[0].vps_type = deploy_type
        vps_infos[0].user = deploy_user
        vps_infos[0].port = deploy_port

        deploy_disk = system_disk
        if not (inst.storage and str(inst.storage).strip()):
            deploy_disk = system_disk
        else:
            try:
                deploy_disk = int(inst.storage)
            except (ValueError, TypeError):
                deploy_disk = system_disk

        req = DeployRequest(
            region_id=region_id,
            vcpus=_coerce_int(inst.cores, "cores"),
            memory=_coerce_int(inst.memory, "memory"),
            disk=deploy_disk,
            vps_infos=vps_infos,
            quota_type=deploy_quota_type,
            quota=deploy_quota,
            bandwidth=deploy_bandwidth,
            group_id=deploy_group_id,
        )
        dc = _get_deploy_client(client, sos_token)
        result = dc.create_deploy(req)
        if result.code == 200:
            click.echo(f"Deployed: {inst.uuid} — {result.msg}")
        else:
            click.echo(f"Created: {inst.uuid} — but deploy failed: [{result.code}] {result.msg}", err=True)
            click.echo(f"Retry manually: ows planet deploy {inst.uuid} --password PWD", err=True)
            sys.exit(1)


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
    if json_output({"total": result.total, "list": [
        {"uuid": i.uuid, "name": i.name, "status": i.status_name, "public_ip": i.public_ip,
         "flavor_name": i.flavor_name, "region_uuid": i.region_uuid} for i in result.list
    ]}):
        return
    header = f"{'UUID':36s}  {'Name':20s}  {'Status':8s}  {'Public IP':15s}  {'Flavor':10s}  {'Region UUID'}"
    click.echo(header)
    click.echo("-" * len(header))
    for inst in result.list:
        click.echo(f"{inst.uuid:36s}  {inst.name:20s}  {inst.status_name:8s}  "
                   f"{inst.public_ip:15s}  {inst.flavor_name:10s}  {inst.region_uuid}")
    click.echo(f"--- {result.total} total")


@planet.command("detail")
@click.argument("uuid", required=False, metavar="INSTANCE_UUID")
@click.option("--project", default=None)
@handle_api_errors
@pass_client
def planet_detail(client, uuid, project):
    """Show instance detail."""
    if not uuid:
        _show_error("Missing INSTANCE_UUID", "ows planet detail <INSTANCE_UUID>", _hint("instance"))
    inst = client.planet.get_detail(uuid, project)
    public_ip = inst.public_port.get("ip", "") if isinstance(inst.public_port, dict) else ""
    if json_output({
        "uuid": inst.uuid, "name": inst.name, "status": inst.status, "status_name": inst.status_name,
        "city_name": inst.city_name, "region_uuid": inst.region_uuid,
        "flavor_name": inst.flavor_name, "cores": inst.cores, "memory": inst.memory,
        "storage": inst.storage, "gpu": inst.gpu,
        "public_ip": public_ip,
        "create_time": inst.create_time, "end_time": inst.end_time,
        "image_uuid": inst.image_uuid, "project_uuid": inst.project_uuid,
        "private_port": inst.private_port, "public_port": inst.public_port,
    }):
        return
    fields = [
        ("UUID", inst.uuid), ("Name", inst.name), ("Status", f"{inst.status_name} ({inst.status})"),
        ("Region", f"{inst.city_name} ({inst.region_uuid})"),
        ("Flavor", inst.flavor_name), ("Cores", inst.cores), ("Memory", inst.memory),
        ("Storage", inst.storage), ("GPU", inst.gpu or "none"),
        ("Public IP", public_ip or "(none)"),
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
        _show_error("Missing INSTANCE_UUID", "ows planet stop <INSTANCE_UUID>", _hint("instance"))
    client.planet.stop(uuid)
    json_output({"ok": True, "action": "stop", "uuid": uuid})


@planet.command("start")
@click.argument("uuid", required=False, metavar="INSTANCE_UUID")
@handle_api_errors
@pass_client
def planet_start(client, uuid):
    """Start an instance."""
    if not uuid:
        _show_error("Missing INSTANCE_UUID", "ows planet start <INSTANCE_UUID>", _hint("instance"))
    client.planet.start(uuid)
    json_output({"ok": True, "action": "start", "uuid": uuid})


@planet.command("reboot")
@click.argument("uuid", required=False, metavar="INSTANCE_UUID")
@click.argument("reboot_type", type=int, required=False)
@handle_api_errors
@pass_client
def planet_reboot(client, uuid, reboot_type):
    """Reboot an instance."""
    if not uuid:
        _show_error("Missing INSTANCE_UUID", "ows planet reboot <INSTANCE_UUID> <REBOOT_TYPE>",
                    _hint("instance"))
    if reboot_type is None:
        _show_error("Missing REBOOT_TYPE", "ows planet reboot <INSTANCE_UUID> <REBOOT_TYPE>")
    client.planet.reboot(uuid, reboot_type)
    json_output({"ok": True, "action": "reboot", "uuid": uuid})
    click.echo(f"Rebooting: {uuid}")


@planet.command("deploy")
@click.argument("uuid", required=False, metavar="INSTANCE_UUID")
@click.option("--sos-token", default="", help="sos_token from dashboard.metrovpn.xyz")
@click.option("--password", default="", help="VPS login password (required)")
@click.option("--vps-id", default="")
@click.option("--os", default="ubuntu 20.04", help="OS label for MetroVPN panel")
@click.option("--type", "vps_type", default="1C-2G", help="Spec label for MetroVPN panel")
@click.option("--user", default="root")
@click.option("--ip", default="")
@click.option("--port", default="22")
@click.option("--brand-id", default="ows.us")
@click.option("--region-id", default="")
@click.option("--vcpus", type=int, default=None)
@click.option("--memory", type=int, default=None)
@click.option("--disk", type=int, default=None)
@click.option("--quota-type", type=int, default=0)
@click.option("--quota", type=int, default=2000)
@click.option("--bandwidth", type=int, default=100)
@click.option("--group-id", default="Vip HighSpeed Server")
@click.option("--vps-infos-json", default="", help="JSON array to override vps_infos")
@handle_api_errors
@pass_client
def planet_deploy(client, uuid, sos_token, password, vps_id, os, vps_type, user, ip, port,
                  brand_id, region_id, vcpus, memory, disk, quota_type, quota, bandwidth,
                  group_id, vps_infos_json):
    """Deploy a Planet instance to MetroVPN."""
    if not uuid:
        _show_error("Missing INSTANCE_UUID", "ows planet deploy <INSTANCE_UUID>", _hint("instance"))
    if not password:
        _show_error("Missing --password", "ows planet deploy <UUID> --password PWD")

    # Get instance: use detail for cores/memory/city/status, use list for public_ip
    inst = _safe_call(client, client.planet.get_detail, uuid)
    if inst.status != 1:
        _show_error(
            f"Instance status is {inst.status_name} ({inst.status}), need Running (1).",
            "ows planet deploy <UUID> --password PWD"
        )

    public_ip = ""

    # Try to get IP from list_instances
    list_result = _safe_call(client, client.planet.list_instances,
                             ListRequest(page_num=1, page_size=200))
    for entry in list_result.list:
        if entry.uuid == uuid:
            public_ip = entry.public_ip
            break

    if not ip:
        ip = public_ip

    if not ip:
        _show_error(
            "Instance has no public IP yet. Wait for creation to complete.",
            f"Check with: ows planet list"
        )

    # Resolve region_id
    if not region_id:
        region_id = _resolve_region_id(inst.city_name)

    # Build vps_infos
    if vps_infos_json:
        vps_data = json.loads(vps_infos_json)
        vps_infos = [VpsLoginInfo(**d) for d in vps_data]
    else:
        vps_infos = _build_vps_infos_from_detail(inst, password)
        info = vps_infos[0]
        if vps_id:
            info.vps_id = vps_id
        if ip:
            info.ip = ip
        info.os = os
        info.vps_type = vps_type
        info.user = user
        info.port = port

    # Validate vps_infos
    if not vps_infos:
        _show_error("vps_infos cannot be empty", "")
    if len(vps_infos) > 5:
        _show_error("vps_infos cannot exceed 5 items", "")

    # Build DeployRequest
    if disk is None and not (inst.storage and str(inst.storage).strip()):
        _show_error(
            "instance storage is empty, please provide --disk (system disk size in GB)",
            "ows planet deploy <UUID> --password PWD --disk 40"
        )
    req = DeployRequest(
        region_id=region_id,
        vcpus=vcpus if vcpus is not None else _coerce_int(inst.cores, "cores"),
        memory=memory if memory is not None else _coerce_int(inst.memory, "memory"),
        disk=disk if disk is not None else _coerce_int(inst.storage, "storage"),
        vps_infos=vps_infos,
        vps_brand_id=brand_id,
        quota_type=quota_type,
        quota=quota,
        bandwidth=bandwidth,
        group_id=group_id,
    )

    # Call deploy
    dc = _get_deploy_client(client, sos_token)
    result = dc.create_deploy(req)
    if result.code == 200:
        if json_output({"ok": True, "uuid": uuid, "action": "deploy", "msg": result.msg}):
            return
        click.echo(f"Deployed: {uuid} — {result.msg}")
    else:
        msg = result.msg or "unknown error"
        if json_output({"ok": False, "uuid": uuid, "action": "deploy",
                        "code": result.code, "msg": msg, "ip": result.ip}):
            return
        click.echo(f"Deploy failed: [{result.code}] {msg}", err=True)
        if result.ip:
            click.echo(f"Failed IP: {result.ip}", err=True)
        sys.exit(1)
