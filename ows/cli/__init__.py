"""ows.us VPS management CLI."""
import functools
import json as _json
import sys

import click

from ows.client import OwsClient
from ows.errors import OwsError

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


def json_output(data):
    """If --json mode, print JSON and return True. Otherwise return False."""
    ctx = click.get_current_context()
    while ctx:
        if ctx.meta.get("ows_json"):
            click.echo(_json.dumps(data, ensure_ascii=False, indent=2, default=str))
            return True
        ctx = ctx.parent
    return False


UUID_SOURCE = {
    "region": "ows product regions",
    "category": "ows planet types",
    "image": "ows planet images --region <REGION_UUID>",
    "flavor": "ows planet flavors --region <REGION_UUID> --category <CATEGORY_UUID>",
    "instance": "ows planet list",
}


def _hint(*keys):
    """Build a multi-line hint listing each UUID and its source."""
    lines = [f"{k} UUID → {UUID_SOURCE[k]}" for k in keys]
    return "\n      ".join(lines)


def _show_error(err_type, usage, hint=None):
    click.echo(f"Error: {err_type}", err=True)
    click.echo(f"Usage: {usage}", err=True)
    if hint:
        click.echo(f"Hint: {hint}", err=True)
    sys.exit(1)


STATUS_MAP = {
    0: "Deleted",
    1: "Running",
    3: "Suspend",
    4: "Down",
    16: "Creating",
    106: "Executing",
}


@click.group()
@click.option("-c", "--config", default="config.json", help="Config file path")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON (for scripts/AI)")
@click.pass_context
def cli(ctx, config, as_json):
    """ows — manage VPS resources via ows.us API."""
    try:
        client = OwsClient.from_config(config)
    except (OwsError, FileNotFoundError, KeyError) as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    ctx.obj = client
    ctx.meta["ows_json"] = as_json


# Register sub-command groups
from ows.cli.planet import planet  # noqa: E402
from ows.cli.product import product  # noqa: E402
from ows.cli.order import order  # noqa: E402

cli.add_command(planet)
cli.add_command(product)
cli.add_command(order)

# Register deploy as top-level command (alias)
from ows.cli.planet import planet_deploy  # noqa: E402
cli.add_command(planet_deploy, name="deploy")
