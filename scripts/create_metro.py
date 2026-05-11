"""Create a Planet instance with Metro default config.

Adjust the CONFIG dict below to change region/flavor/image/project.
"""
import random, string, time
from ows.client import OwsClient
from ows.models import CreateRequest

# ---- 可修改的默认配置 ----
CONFIG = {
    "category_keyword": "Shared vCPU",
    "region_city": "SIN",         # 城市码前缀
    "image_keyword": "ubuntu 20", # 镜像名称（小写匹配）
    "flavor_cores": 1,
    "flavor_memory": 2,
    "project_name": "metro",      # 项目名称（小写匹配）
    "system_disk": 40,
    "billing_model": 2,           # 1=包月, 2=按量
    "service_period": 1,
}
# -------------------------

client = OwsClient.from_config("config.json")

# 1. 产品分类
types = client.planet.get_planet_type()
kw = CONFIG["category_keyword"].lower()
cat = next((t for t in types if kw in t.name.lower()), None)
cat_uuid = cat.category_uuid
print(f"[category] {cat.name} → {cat_uuid}")
time.sleep(1)

# 2. 区域
regions = client.product.get_region()
region_uuid = None
city = CONFIG["region_city"].upper()
for r in regions:
    for child in r.children:
        for z in child.get("zone", []):
            if city in z.get("city_code", "").upper():
                region_uuid = z["region_uuid"]
                print(f"[region] {child.get('name')} ({z.get('city_code')}) → {region_uuid}")
                break
time.sleep(1)

# 3. 镜像
images = client.planet.get_image_by_region(region_uuid)
img_kw = CONFIG["image_keyword"].lower()
img = None
for group in images:
    for i in group.images:
        if img_kw in i.get("name", "").lower():
            img = i; break
    if img: break
img_uuid = img["uuid"]
print(f"[image] {img['name']} → {img_uuid}")
time.sleep(1)

# 4. 规格
flavors = client.planet.get_flavor_by_add(region_uuid, cat_uuid)
c, m = CONFIG["flavor_cores"], CONFIG["flavor_memory"]
flavor = next((f for f in flavors if f.cores == c and f.memory == m), None)
flavor_uuid = flavor.uuid
print(f"[flavor] {flavor.name} ({flavor.cores}c{flavor.memory}g) → {flavor_uuid}")
time.sleep(1)

# 5. 项目
projects = client.post("/console/userProject/getList", {})
if isinstance(projects, dict):
    projects = projects.get("list", projects.get("data", []))
pn = CONFIG["project_name"].lower()
proj = next((p for p in projects if p.get("name", "").lower() == pn), None)
proj_uuid = proj["uuid"] if proj else ""
print(f"[project] {CONFIG['project_name']} → {proj_uuid}")
time.sleep(2)

# 6. 密码
special = "!@#$%^&*"
pwd = [random.choice(string.ascii_uppercase),
       random.choice(string.ascii_lowercase),
       random.choice(string.digits),
       random.choice(special)]
allc = string.ascii_letters + string.digits + special
pwd += [random.choice(allc) for _ in range(12)]
random.shuffle(pwd)
password = "".join(pwd)

# 7. 名称
suffix = "".join(random.choices(string.ascii_letters + string.digits, k=6))
name = f"Planet-{CONFIG['region_city']}01-{suffix}"
print(f"[password] {password}")
print(f"[name] {name}")

# 8. 创建
print("\n--- Creating ---")
req = CreateRequest(
    region_uuid=region_uuid, flavor_uuid=flavor_uuid, image_uuid=img_uuid,
    system_disk=CONFIG["system_disk"],
    billing_model=CONFIG["billing_model"],
    service_period=CONFIG["service_period"],
    project_uuid=proj_uuid, name=name, adminPass=password,
)
time.sleep(2)
result = client.planet.create(req)
print(f"UUID: {result.uuid or '(异步创建，稍后通过 list 查看)'}")
print(f"Name: {name}")
print(f"Password: {password}")
