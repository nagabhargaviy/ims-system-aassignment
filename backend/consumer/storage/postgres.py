import json
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="ims_db",
    user="ims",
    password="ims"
)

conn.autocommit = True
cursor = conn.cursor()


def create_work_item(component_id):
    cursor.execute(
        "INSERT INTO work_items (component_id, status) VALUES (%s, %s) RETURNING id",
        (component_id, "OPEN")
    )
    return cursor.fetchone()[0]


def store_signal(work_item_id, signal):
    cursor.execute(
        "INSERT INTO signals (work_item_id, payload) VALUES (%s, %s)",
        (work_item_id, json.dumps(signal))
    )


def create_rca(work_item_id, root_cause, fix):
    cursor.execute(
        "INSERT INTO rca (work_item_id, root_cause, fix) VALUES (%s, %s, %s)",
        (work_item_id, root_cause, fix)
    )


def get_rca(work_item_id):
    cursor.execute(
        "SELECT * FROM rca WHERE work_item_id = %s",
        (work_item_id,)
    )
    return cursor.fetchone()


def update_status(work_item_id, status):
    cursor.execute(
        "UPDATE work_items SET status = %s WHERE id = %s",
        (status, work_item_id)
    )