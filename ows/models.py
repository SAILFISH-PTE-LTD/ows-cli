from dataclasses import dataclass, field
from typing import List, Generic, TypeVar

T = TypeVar("T")


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
    images: str = ""
    uuid: str = ""


@dataclass
class Flavor:
    uuid: str
    name: str
    cores: str = ""
    memory: str = ""
    storage: str = ""
    nic: str = ""
    gpu: str = ""
    h_price: float = 0.0
    m_price: float = 0.0
    h_discount_price: float = 0.0
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
    flavor_name: str = ""
    model: str = ""
    cores: str = ""
    memory: str = ""
    storage: str = ""
    nic: str = ""
    gpu: str = ""
    name: str = ""
    region_uuid: str = ""
    region_name: str = ""
    status: int = 0
    status_name: str = ""
    create_time: str = ""
    private_ip: str = ""
    public_ip: str = ""
    public_ipv6: str = ""
    image_name: str = ""
    os_icon_type: str = ""
    project_uuid: str = ""
    billing_model: int = 0
    service_period: int = 0
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
