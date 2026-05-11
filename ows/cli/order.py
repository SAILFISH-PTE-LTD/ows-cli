"""ows order — billing records."""
import calendar
import time as _time
import click
from ows.cli import handle_api_errors, json_output, pass_client
from ows.models import OrderListRequest, BillMonthRequest
from ows.api.order import ORDER_STATUS
from ows.api.bill import BILL_TYPE


@click.group()
def order():
    """Billing records."""
    pass


@order.command("billing")
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
def order_billing(client, **kwargs):
    """List billing records (charge history)."""
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


@order.command("detail")
@click.option("--month", default="", help="Month (YYYY-MM)")
@click.option("--team-uuid", default="", help="Team UUID")
@click.option("--invoice", is_flag=True, help="Output in invoice JSON format")
@pass_client
@handle_api_errors
def order_detail(client, month, team_uuid, invoice):
    """Monthly bill detail (by resource)."""
    if not month:
        click.echo("Usage: ows order detail --month YYYY-MM")
        click.echo("Example: ows order detail --month 2026-05")
        return
    try:
        y, m = map(int, month.split("-"))
        begin_dt = _time.strptime(f"{y}-{m:02d}-01", "%Y-%m-%d")
        begin = int(_time.mktime(begin_dt))
        if m == 12:
            end_dt = _time.strptime(f"{y + 1}-01-01", "%Y-%m-%d")
        else:
            end_dt = _time.strptime(f"{y}-{m + 1:02d}-01", "%Y-%m-%d")
        end = int(_time.mktime(end_dt)) - 1
    except (ValueError, TypeError):
        click.echo("Error: --month must be YYYY-MM, e.g. --month 2026-05", err=True)
        return

    data = client.bill.get_detail_by_month(BillMonthRequest(
        begin_date=str(begin), end_date=str(end), team_uuid=team_uuid,
    ))

    if invoice:
        try:
            from ows_deploy.bill import output_invoice
            click.echo(output_invoice(data, y, m))
        except ImportError:
            click.echo("Error: ows_deploy module not found. Install ows_deploy/ for --invoice support.", err=True)
        return

    if json_output({
        "invid": data.invid, "user_total_money": data.user_total_money,
        "total_gift": data.total_gift, "list": [
            {
                "sid": i.sid, "region_id": i.region_id, "region_name": i.region_name,
                "total_money": i.total_money, "total": i.total, "quantity": i.quantity,
                "type": i.type, "name": i.name, "product_name": i.product_name,
                "product_type": i.product_type, "ip": i.ip,
                "start_time": i.start_time, "end_time": i.end_time,
                "max_quantity": i.max_quantity, "description": i.description,
            } for i in data.list
        ],
    }):
        return
    if not data.list:
        click.echo("No bill data found.")
        return
    click.echo(f"{'Name':<22} {'Region':<8} {'IP':<16} {'Type':<10} {'Money':>12} {'Duration'}")
    click.echo("-" * 100)
    for i in data.list:
        type_name = BILL_TYPE.get(i.type, f"Type{i.type}")
        name = i.name or i.description or "-"
        money = f"{float(i.total_money):.2f} USD"
        dur = f"{i.total} x10min"
        click.echo(f"{name:<22} {i.region_name:<8} {i.ip:<16} {type_name:<10} {money:>12}   {dur}")
    click.echo()
    click.echo(f"Total: {data.user_total_money} USD  |  Gift: {data.total_gift} USD  |  Invoice: {data.invid}")
