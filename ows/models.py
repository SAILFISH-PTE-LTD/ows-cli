from dataclasses import dataclass, field, fields as dc_fields
from typing import List, Generic, TypeVar, Type

T = TypeVar("T")


def _from_dict(cls: Type[T], data: dict) -> T:
    """Construct a dataclass from a dict, ignoring unknown keys, coercing types."""
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


@dataclass
class ListResult(Generic[T]):
    list: List[T]
    total: int = 0


@dataclass
class StatusResult:
    status: int


@dataclass
class CreateResult:
    uuid: str


# --- Planet: info ---

@dataclass
class PlanetType:
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
    id: int
    name: str
    icon_type: str = ""
    type: int = 0
    images: list = field(default_factory=list)


@dataclass
class Flavor:
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


# --- Planet: price ---

@dataclass
class DataDisk:
    name: str = ""
    disk_size: int = 0
    disk_type: int = 0


@dataclass
class PriceRequest:
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


# --- Planet: instance ---

@dataclass
class CreateRequest:
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


# --- Deploy ---

@dataclass
class VpsLoginInfo:
    vps_id: str
    password: str
    ip: str
    os: str = "ubuntu 20.04"
    vps_type: str = "1C-2G"
    user: str = "root"
    port: str = "22"


@dataclass
class DeployRequest:
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
    code: int
    msg: str = ""
    ip: str = ""


# --- Order ---

@dataclass
class Order:
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
    page_num: int = 1
    page_size: int = 10
    status: int = 0
    product_type: int = 0
    begin_date: str = ""
    end_date: str = ""
    is_renew: int = 0
    ctime_sort: int = 0
    etime_sort: int = 0
