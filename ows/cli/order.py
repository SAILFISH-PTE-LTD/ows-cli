"""ows order — billing records."""
import click
from ows.cli import handle_api_errors, json_output, pass_client
from ows.models import OrderListRequest
from ows.api.order import ORDER_STATUS


@click.group()
def order():
    """Billing records."""
    pass


@order.command("list")
@click.option("--status", type=int, default=0, help="0=Not Paid 1=Paid 2=Expired 3=Deleted")
@click.option("--product-type", "product_type", type=int, default=0, help="Product type")
@click.option("--page", "page_num", type=int, default=1, help="Page number")
@click.option("--page-size", "page_size", type=int, default=20, help="Items per page")
@click.option("--begin-date", default="", help="Start date (YYYY-MM-DD)")
@click.option("--end-date", default="", help="End date (YYYY-MM-DD)")
@click.option("--sort-time", "time_sort", type=int, default=0, help="Sort by time")
@click.option("--sort-price", "price_sort", type=int, default=0, help="Sort by price")
@pass_client
@handle_api_errors
def order_list(client, **kwargs):
    """List billing records."""
    data = client.order.list_orders(OrderListRequest(**kwargs))
    if json_output({"total": data.total, "list": [
        {
            "id": o.id, "order_sn": o.order_sn, "status": o.status,
            "type": o.type, "product_type": o.product_type,
            "amount": o.amount, "discount": o.discount,
            "original_price": o.original_price, "create_time": o.ctime,
            "remark": o.remark, "boss_remark": o.boss_remark,
        } for o in data.list
    ]}):
        return
    if not data.list:
        click.echo("No billing records found.")
        return
    click.echo(f"{'ID':<8} {'Order SN':<22} {'Type':<6} {'Prod':<6} {'Status':<10} {'Amount':>10} {'Created'}")
    click.echo("-" * 100)
    for o in data.list:
        status_name = ORDER_STATUS.get(o.status, str(o.status))
        click.echo(f"{o.id:<8} {o.order_sn:<22} {o.type:<6} {o.product_type:<6} {status_name:<10} {o.amount:>8.2f}   {o.ctime}")
    click.echo()
    click.echo(f"Total: {data.total}  |  Page: {kwargs['page_num']}  |  Showing: {len(data.list)}")
