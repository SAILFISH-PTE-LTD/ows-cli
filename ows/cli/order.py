"""ows order — manage orders."""
import click
from ows.cli import handle_api_errors, json_output, pass_client
from ows.models import OrderListRequest
from ows.api.order import ORDER_STATUS, ORDER_TYPE, ORDER_PRODUCT_TYPE


@click.group()
def order():
    """Manage orders."""
    pass


@order.command("list")
@click.option("--status", type=int, default=0, help="Order status (0=Unpaid 1=Paid 2=Cancelled 3=Refunded)")
@click.option("--product-type", "product_type", type=int, default=0, help="Product type (1=ECS 2=BareMetal)")
@click.option("--page", "page_num", type=int, default=1, help="Page number")
@click.option("--page-size", "page_size", type=int, default=20, help="Items per page")
@click.option("--begin-date", default="", help="Start date (YYYY-MM-DD)")
@click.option("--end-date", default="", help="End date (YYYY-MM-DD)")
@click.option("--sort-ctime", "ctime_sort", type=int, default=0, help="Sort by create time (0=desc 1=asc)")
@click.option("--sort-etime", "etime_sort", type=int, default=0, help="Sort by end time (0=desc 1=asc)")
@pass_client
@handle_api_errors
def order_list(client, **kwargs):
    """List orders."""
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
        click.echo("No orders found.")
        return
    click.echo(f"{'ID':<8} {'Order SN':<22} {'Type':<8} {'Product':<12} {'Status':<10} {'Amount':>10} {'Created'}")
    click.echo("-" * 110)
    for o in data.list:
        type_name = ORDER_TYPE.get(o.type, str(o.type))
        prod_name = ORDER_PRODUCT_TYPE.get(o.product_type, str(o.product_type))
        status_name = ORDER_STATUS.get(o.status, str(o.status))
        click.echo(f"{o.id:<8} {o.order_sn:<22} {type_name:<8} {prod_name:<12} {status_name:<10} {o.amount:>8.2f}   {o.ctime}")
    click.echo()
    click.echo(f"Total: {data.total}  |  Page: {kwargs['page_num']}  |  Showing: {len(data.list)}")
