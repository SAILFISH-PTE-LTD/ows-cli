"""Quick script: list instances to check if creation worked."""
from ows.client import OwsClient
from ows.models import ListRequest

client = OwsClient.from_config("config.json")
result = client.planet.list_instances(ListRequest(page_size=10, page_num=1))
print(f"Total: {result.total}")
for inst in result.list:
    print(f"  {inst.uuid}  {inst.name:25s}  {inst.status_name}  {inst.create_time}")
