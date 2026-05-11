"""Delete all 6 accidentally-created SIN instances."""
import time
from ows.client import OwsClient

uuids = [
    "7e1c21c9-ac0f-5f52-9fa2-cd0410183860",
    "e28ae401-e513-5737-8095-df489b6acc72",
    "aff3adba-cb80-5905-9fca-df7dc5e66e77",
    "35a56831-975e-53f3-9562-cce628d060e9",
    "73289cde-a5c3-5d9e-bb8e-4f777f0e624a",
    "8d35d79e-b66d-5ebd-8ad6-be51b40492b5",
]

client = OwsClient.from_config("config.json")
for uuid in uuids:
    client.product.free(uuid)
    print(f"Freed: {uuid}")
    time.sleep(2)
print("Done.")
