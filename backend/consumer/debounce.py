import redis
import time

r = redis.Redis(host="localhost", port=6379, decode_responses=True)

def get_or_create_key(component_id: str):
    window = int(time.time() / 10)
    key = f"{component_id}:{window}"

    return key


def get_existing_work_id(key):
    return r.get(key)


def set_work_id(key, work_id):
    r.setex(key, 10, work_id)