"""Data models for ows.us API requests and responses.

All models are dataclasses.  Use :func:`_from_dict` to construct instances
from API JSON responses — it gracefully ignores unknown fields and coerces
string→float where needed.
"""

from dataclasses import dataclass, field, fields as dc_fields
from typing import List, Generic, TypeVar, Type

T = TypeVar("T")


def _from_dict(cls: Type[T], data: dict) -> T:
    """Construct a dataclass from a dictionary.

    Ignores keys not matching dataclass fields.  Coerces ``str`` → ``float``
    when the field type annotation is ``float``.

    Args:
        cls: Target dataclass type.
        data: Raw API response dictionary.

    Returns:
        An instance of *cls* populated from *data*.
    """
    known = {f.name: f for f in dc_fields(cls)}
    filtered = {}
    for k, v in data.items():
        if k not in known:
            continue
        ftype = known[k].type
        if ftype is float and isinstance(v, str):
            filtered[k] = float(v)
        else:
            filtered[k] = v
    return cls(**filtered)


# ---------------------------------------------------------------------------
# Generic helpers
# ---------------------------------------------------------------------------


@dataclass
class ListResult(Generic[T]):
    """Paginated list result.

    Fields:
        list: Items for the current page.
        total: Total number of matching items across all pages.
    """
    list: List[T]
    total: int = 0


@dataclass
class StatusResult:
    """Resource status result.

    Fields:
        status:      Status code (0=Deleted, 1=Running, 3=Suspend, 4=Down,
                     16=Creating, 106=Executing).
    """
    status: int


@dataclass
class CreateResult:
    """Create operation result.

    Fields:
        uuid: Instance UUID.  May be empty — creation is asynchronous.
    """
    uuid: str


# ---------------------------------------------------------------------------
# Planet: info
# ---------------------------------------------------------------------------


@dataclass
class PlanetType:
    """Product category.

    Fields:
        category_uuid:  Category UUID.
        name:           Display name (e.g. "Shared vCPU").
        status:         Category status.
        product_type:   Product type code.
        description:    Category description.
        flag_code:      Region flag code.
        billing_model:  Supported billing models.
        service_period: Service period (months).
    """
    category_uuid: str
    name: str
    status: int
    product_type: int = 0
    description: str = ""
    flag_code: str = ""
    billing_model: str = ""
    service_period: int = 0


@dataclass
class Image:
    """OS image group.

    Each *Image* contains an ``images`` list of individual image dicts,
    each with keys ``name``, ``uuid``, ``id``.

    Fields:
        id:        Image group ID.
        name:      Group name (e.g. "Ubuntu").
        icon_type: Icon type label.
        type:      Image type code.
        images:    List of image dicts (``name``, ``uuid``, ``id``).
    """
    id: int
    name: str
    icon_type: str = ""
    type: int = 0
    images: list = field(default_factory=list)


@dataclass
class Flavor:
    """Instance specification (vCPU + memory).

    Fields:
        uuid:               Flavor UUID.
        name:               Human-readable name ("1C-2G").
        id:                 Flavor ID.
        cores:              vCPU count.
        memory:             Memory in GB.
        h_price:            Hourly price (USD).
        m_price:            Monthly price (USD).
        h_discount_price:   Discounted hourly price.
        m_discount_price:   Discounted monthly price.
        free_flow:          Included free traffic.
        status:             Availability status.
    """
    uuid: str
    name: str
    id: int = 0
    cores: int = 0
    memory: int = 0
    h_price: float = 0.0
    m_price: float = 0.0
    h_discount_price: float = 0.0
    m_discount_price: float = 0.0
    free_flow: int = 0
    status: int = 0


# ---------------------------------------------------------------------------
# Planet: price
# ---------------------------------------------------------------------------


@dataclass
class DataDisk:
    """Additional data disk specification.

    Fields:
        name:       Disk display name.
        disk_size:  Size in GB.
        disk_type:  Disk type code (1=SSD).
    """
    name: str = ""
    disk_size: int = 0
    disk_type: int = 0


@dataclass
class PriceRequest:
    """Parameters for :meth:`PlanetAPI.get_price`.

    Fields:
        region_uuid:     Region UUID.
        flavor_uuid:     Flavor UUID.
        image_uuid:      Image UUID.
        system_disk:     System disk size (GB).
        billing_model:   ``1`` = monthly, ``2`` = pay-as-you-go.
        service_period:  Duration (months for billing_model=1; ``1`` for
                         billing_model=2).
        data_disk:       Additional data disks.
        coupon_id:       Coupon ID (0 = none).
        user_time:       Purchase duration override (0 = default).
    """
    region_uuid: str
    flavor_uuid: str
    image_uuid: str
    system_disk: int
    billing_model: int
    service_period: int
    data_disk: List[DataDisk] = field(default_factory=list)
    coupon_id: int = 0
    user_time: int = 0


@dataclass
class PriceResult:
    """Price breakdown returned by :meth:`PlanetAPI.get_price`.

    All prices are in USD.

    Fields:
        flavor_price:        Flavor base price.
        system_disk_price:   System disk price.
        data_disk_price:     Data disk total price.
        flow_price:          Traffic price.
        ip_price:            IP address price.
        image_price:         Image price.
        total_price:         Total after discounts and coupons.
        original_price:      Original total before discounts.
        discount_price:      Discount amount.
        coupon_price:        Coupon amount.
    """
    flavor_price: float = 0.0
    system_disk_price: float = 0.0
    data_disk_price: float = 0.0
    flow_price: float = 0.0
    ip_price: float = 0.0
    image_price: float = 0.0
    total_price: float = 0.0
    original_price: float = 0.0
    discount_price: float = 0.0
    coupon_price: float = 0.0


# ---------------------------------------------------------------------------
# Planet: instance
# ---------------------------------------------------------------------------


@dataclass
class CreateRequest:
    """Parameters for :meth:`PlanetAPI.create`.

    Fields:
        region_uuid:           Region UUID.
        flavor_uuid:           Flavor UUID.
        image_uuid:            Image UUID.
        system_disk:           System disk size (GB).
        billing_model:         ``1`` = monthly, ``2`` = pay-as-you-go.
        service_period:        Duration (months or ``1``).
        project_uuid:          Project UUID.
        name:                  Instance display name; auto-generated if empty.
        data_disk:             Additional data disks.
        remark:                Remark / note.
        adminPass:             Admin password.  Auto-generated if empty.
                               Must contain upper + lower + digit + special.
        ssh_key:               SSH public key.
        security_group_uuid:   Security group UUID.
        coupon_id:             Coupon ID.
        user_time:             Purchase duration override.
        is_renew:              Auto-renew flag.
        is_backup:             Backup flag.
        app_market_uuid:       Application market image UUID.
        app_market_base_data:  Application market base data.
    """
    region_uuid: str
    flavor_uuid: str
    image_uuid: str
    system_disk: int
    billing_model: int
    service_period: int
    project_uuid: str = ""
    name: str = ""
    data_disk: List[DataDisk] = field(default_factory=list)
    remark: str = ""
    adminPass: str = ""
    ssh_key: str = ""
    security_group_uuid: str = ""
    coupon_id: int = 0
    user_time: int = 0
    is_renew: int = 0
    is_backup: int = 0
    app_market_uuid: str = ""
    app_market_base_data: str = ""


@dataclass
class ListRequest:
    """Parameters for :meth:`PlanetAPI.list_instances`.

    Fields:
        page_num:        Page number (1-indexed).
        page_size:       Items per page.
        region_uuid:     Filter by region UUID.
        project_uuid:    Filter by project UUID.
        begin_date:      Filter by start date.
        end_date:        Filter by end date.
        status:          Filter by status string.
        ctime_sort:      Sort by creation time.
        etime_sort:      Sort by end time.
        name:            Filter by instance name.
        ip:              Filter by IP address.
        keyword:         Keyword search.
        app_market_type: Application market type filter.
    """
    page_num: int = 1
    page_size: int = 10
    region_uuid: str = ""
    project_uuid: str = ""
    begin_date: str = ""
    end_date: str = ""
    status: str = ""
    ctime_sort: int = 0
    etime_sort: int = 0
    name: str = ""
    ip: str = ""
    keyword: str = ""
    app_market_type: str = ""


@dataclass
class Instance:
    """Instance summary (returned by :meth:`PlanetAPI.list_instances`).

    Key fields:

    Fields:
        uuid:            Instance UUID.
        name:            Display name.
        flavor_name:     Flavor name ("1C-2G", ...).
        public_ip:       Public IPv4 address.
        status:          Numeric status code.
        status_name:     Human-readable status.
        region_uuid:     Region UUID.
        city_name:       City name.
        city_code:       City code ("SIN", "TPE", ...).
        create_time:     Creation timestamp string.
        end_time:        Expiration Unix timestamp.
    """
    uuid: str = ""
    sid: int = 0
    uid: int = 0
    flavor_name: str = ""
    flavor_uuid: str = ""
    model: str = ""
    model_id: int = 0
    cores: str = ""
    memory: str = ""
    storage: str = ""
    nic: str = ""
    gpu: str = ""
    name: str = ""
    host: str = ""
    region_uuid: str = ""
    region_name: str = ""
    region_id: int = 0
    city_name: str = ""
    city_code: str = ""
    status: int = 0
    status_name: str = ""
    system_type: int = 0
    create_time: str = ""
    stop_time: int = 0
    delete_time: int = 0
    end_time: int = 0
    private_ip: list = field(default_factory=list)
    public_ip: str = ""
    public_ipv6: str = ""
    image_id: int = 0
    image_name: str = ""
    image_uuid: str = ""
    os_icon_type: str = ""
    project_uuid: str = ""
    billing_model: int = 0
    service_period: int = 0
    amount: int = 0
    bandwidth_cap: int = 0
    speed_type: int = 0
    is_enable_security_group: int = 0
    is_own: int = 0
    product_type: int = 0
    app_market_type: str = ""
    email: str = ""
    username: str = ""
    data_disk: list = field(default_factory=list)


@dataclass
class InstanceDetail:
    """Full instance detail (returned by :meth:`PlanetAPI.get_detail`).

    Key fields:

    Fields:
        uuid:           Instance UUID.
        name:           Display name.
        flavor_name:    Flavor name.
        cores:          vCPU count (str from API).
        memory:         Memory in GB (str from API).
        storage:        Storage size (str from API).
        status:         Numeric status code.
        status_name:    Human-readable status.
        city_name:      City name.
        city_code:      City code.
        public_ip:      Public IPv4 address.
        public_port:    Dict with ``ip`` and ``port`` keys.
        private_port:   Internal port info dict.
        create_time:    Creation time string.
        end_time:       Expiration Unix timestamp.
        region_uuid:    Region UUID.
        image_uuid:     Image UUID.
        flavor_uuid:    Flavor UUID.
        project_uuid:   Project UUID.
        gpu:            GPU info (empty if none).
        data_disk:      Data disk list.
        subnet:         Subnet list.
        security_group: Security group list.
    """
    uuid: str = ""
    region_uuid: str = ""
    image_uuid: str = ""
    flavor_uuid: str = ""
    flavor_name: str = ""
    cores: str = ""
    memory: str = ""
    storage: str = ""
    nic: str = ""
    gpu: str = ""
    name: str = ""
    system_type: str = ""
    city_name: str = ""
    city_code: str = ""
    public_ip: str = ""
    status: int = 0
    status_name: str = ""
    create_time: str = ""
    end_time: str = ""
    project_uuid: str = ""
    free_flow: int = 0
    is_backup: int = 0
    backup_open_status: int = 0
    private_port: dict = field(default_factory=dict)
    public_port: dict = field(default_factory=dict)
    data_disk: list = field(default_factory=list)
    subnet: list = field(default_factory=list)
    security_group: list = field(default_factory=list)
    app_market: list = field(default_factory=list)


# ---------------------------------------------------------------------------
# Deploy
# ---------------------------------------------------------------------------


@dataclass
class VpsLoginInfo:
    """Single VPS login info for deploy.

    Fields:
        vps_id:    VPS identifier (instance UUID).
        password:  Login password.
        ip:        Public IP address.
        os:        OS label ("ubuntu 20.04").
        vps_type:  Spec label ("1C-2G").
        user:      SSH user ("root").
        port:      SSH port ("22").
    """
    vps_id: str
    password: str
    ip: str
    os: str = "ubuntu 20.04"
    vps_type: str = "1C-2G"
    user: str = "root"
    port: str = "22"


@dataclass
class DeployRequest:
    """Parameters for :meth:`DeployClient.create_deploy`.

    Fields:
        region_id:    Deploy region ID ("Tokyo (Japan)", ...).
        vcpus:        vCPU count.
        memory:       Memory in MB.
        disk:         Disk size in GB.
        vps_infos:    List of VPS login info entries (max 5).
        vps_brand_id: Brand label.
        quota_type:   Quota type.
        quota:        Quota value.
        bandwidth:    Bandwidth in Mbps.
        group_id:     Target group name.
        tag:          Tag label.
    """
    region_id: str
    vcpus: int
    memory: int
    disk: int
    vps_infos: List[VpsLoginInfo]
    vps_brand_id: str = "ows.us"
    quota_type: int = 0
    quota: int = 2000
    bandwidth: int = 100
    group_id: str = "Vip HighSpeed Server"
    tag: str = "metro"


@dataclass
class DeployResult:
    """Result from :meth:`DeployClient.create_deploy`.

    Fields:
        code:  Response code (200 = success).
        msg:   Response message.
        ip:    IP address that failed (if any).
    """
    code: int
    msg: str = ""
    ip: str = ""


# ---------------------------------------------------------------------------
# Order
# ---------------------------------------------------------------------------


@dataclass
class Order:
    """Billing order / charge record.

    Fields:
        id:              Order ID.
        order_sn:        Order serial number.
        status:          Order status (0=Not Paid, 1=Paid, 2=Expired,
                         3=Deleted).
        type:            Order type.
        product_type:    Product type code.
        amount:          Order amount (USD).
        original_price:  Original price before discount.
        discount:        Discount amount.
        ctime:           Creation time string.
        utime:           Update time string.
        remark:          User remark.
        boss_remark:     Administrator remark.
    """
    id: int = 0
    uid: int = 0
    order_sn: str = ""
    payid: int = 0
    status: int = 0
    type: int = 0
    product_type: int = 0
    product_info: str = ""
    original_price: float = 0.0
    amount: float = 0.0
    discount: float = 0.0
    ctime: str = ""
    utime: str = ""
    create_time: int = 0
    update_time: int = 0
    delete_time: int = 0
    remark: str = ""
    boss_remark: str = ""


@dataclass
class OrderListRequest:
    """Parameters for :meth:`OrderAPI.list_orders`.

    Fields:
        page_num:     Page number (1-indexed).
        page_size:    Items per page.
        status:       Order status filter (0=Not Paid, 1=Paid, 2=Expired,
                      3=Deleted).
        product_type: Product type filter.
        begin_date:   Start date string ("" = no filter).
        end_date:     End date string ("" = no filter).
        time_sort:    Sort by time.
        price_sort:   Sort by price.
    """
    page_num: int = 1
    page_size: int = 10
    status: int = 0
    product_type: int = 0
    begin_date: str = ""
    end_date: str = ""
    time_sort: int = 0
    price_sort: int = 0


# ---------------------------------------------------------------------------
# Bill
# ---------------------------------------------------------------------------


@dataclass
class BillItem:
    """Single line item in a monthly bill.

    Fields:
        sid:            Instance ID (0 for non-instance items like traffic).
        region_id:      Region ID.
        total_money:    Cost in USD (string from API).
        start_time:     Billing start Unix timestamp.
        end_time:       Billing end Unix timestamp.
        total:          Billing duration (10-min units).
        quantity:       Billing quantity.
        type:           Item type (1=Instance, 2=Traffic).
        name:           Instance name.
        product_name:   Product type name ("ECS").
        ip:             Instance IP address.
        region_name:    Region display name.
        description:    Item description.
    """
    sid: int = 0
    region_id: int = 0
    total_money: str = "0"
    start_time: int = 0
    end_time: int = 0
    total: int = 0
    quantity: int = 0
    display_value: str = "0"
    max_quantity: int = 0
    type: int = 0
    server_end_time: int = 0
    product_info: str = ""
    name: str = ""
    product_type: int = 0
    product_name: str = ""
    ip: str = ""
    region_name: str = ""
    description: str = ""


@dataclass
class BillDetail:
    """Monthly bill detail.

    Fields:
        list:             Bill line items.
        invid:            Invoice ID.
        user_total_money: Total cost in USD.
        total_gift:       Total gift/credit.
    """
    list: List[BillItem] = field(default_factory=list)
    invid: str = ""
    user_total_money: str = "0"
    total_gift: str = "0"


@dataclass
class BillMonthRequest:
    """Parameters for :meth:`BillAPI.get_detail_by_month`.

    Fields:
        begin_date:  Billing period start (Unix timestamp string).
        end_date:    Billing period end (Unix timestamp string).
        team_uuid:   Team UUID ("" = default team).
    """
    begin_date: str = ""
    end_date: str = ""
    team_uuid: str = ""
