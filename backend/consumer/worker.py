from kafka import KafkaConsumer
import json

from backend.consumer.debounce import get_or_create_key, get_existing_work_id, set_work_id
from backend.consumer.storage.postgres import create_work_item, store_signal

consumer = KafkaConsumer(
    "signals",
    bootstrap_servers="localhost:9092",
    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    group_id="ims-group"
)

print("Consumer started...")

for message in consumer:
    signal = message.value
    component_id = signal.get("component_id")

    key = get_or_create_key(component_id)
    work_id = get_existing_work_id(key)

    if not work_id:
        work_id = create_work_item(component_id)
        set_work_id(key, work_id)
        print(f"CREATED INCIDENT ID: {work_id}")
    else:
        print(f"+ USING EXISTING INCIDENT ID: {work_id}")

    store_signal(work_id, signal)