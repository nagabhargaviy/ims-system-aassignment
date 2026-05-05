from fastapi import FastAPI, Request
from fastapi.responses import Response
from kafka import KafkaProducer
import json
import psycopg2
from backend.models.state_machine import WorkItemStateMachine
from prometheus_client import Counter, generate_latest

app = FastAPI()

# -------------------------------
# Kafka Producer
# -------------------------------
producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

# -------------------------------
# Postgres Connection
# -------------------------------
conn = psycopg2.connect(
    host="localhost",
    database="ims_db",
    user="ims",
    password="ims"
)
conn.autocommit = True
cursor = conn.cursor()

# -------------------------------
# Metrics
# -------------------------------
REQUEST_COUNT = Counter("requests_total", "Total API Requests")

# -------------------------------
# Health
# -------------------------------
@app.get("/health")
def health():
    REQUEST_COUNT.inc()
    return {"status": "ok"}


# -------------------------------
# Ingest Signal
# -------------------------------
@app.post("/signals")
async def ingest_signal(request: Request):
    REQUEST_COUNT.inc()
    data = await request.json()
    producer.send("signals", data)
    return {"status": "queued"}


# -------------------------------
# Get All Incidents
# -------------------------------
@app.get("/incidents")
def get_incidents():
    REQUEST_COUNT.inc()
    cursor.execute("SELECT * FROM work_items ORDER BY created_at DESC")
    rows = cursor.fetchall()

    return [
        {
            "id": r[0],
            "component_id": r[1],
            "status": r[2],
            "created_at": str(r[3])
        }
        for r in rows
    ]


# -------------------------------
# Get Incident Details
# -------------------------------
@app.get("/incidents/{incident_id}")
def get_incident(incident_id: int):
    REQUEST_COUNT.inc()

    cursor.execute(
        "SELECT * FROM work_items WHERE id = %s",
        (incident_id,)
    )
    work = cursor.fetchone()

    if not work:
        return {"error": "incident not found"}

    cursor.execute(
        "SELECT payload FROM signals WHERE work_item_id = %s",
        (incident_id,)
    )
    signals = cursor.fetchall()

    return {
        "id": work[0],
        "component_id": work[1],
        "status": work[2],
        "signals": [s[0] for s in signals]
    }


# -------------------------------
# Add / Update RCA (UPSERT)
# -------------------------------
@app.post("/incidents/{incident_id}/rca")
async def add_rca(incident_id: int, request: Request):
    REQUEST_COUNT.inc()

    data = await request.json()
    root_cause = data.get("root_cause")
    fix = data.get("fix")

    if not root_cause or not fix:
        return {"error": "missing fields"}

    cursor.execute(
        """
        INSERT INTO rca (work_item_id, root_cause, fix)
        VALUES (%s, %s, %s)
        ON CONFLICT (work_item_id)
        DO UPDATE SET root_cause = EXCLUDED.root_cause,
                      fix = EXCLUDED.fix
        """,
        (incident_id, root_cause, fix)
    )

    return {"status": "rca upserted"}


# -------------------------------
# Resolve Incident
# -------------------------------
@app.post("/incidents/{incident_id}/resolve")
def resolve_incident(incident_id: int):
    REQUEST_COUNT.inc()

    cursor.execute(
        "SELECT status FROM work_items WHERE id = %s",
        (incident_id,)
    )
    result = cursor.fetchone()

    if not result:
        return {"error": "incident not found"}

    state = result[0]
    sm = WorkItemStateMachine(state)

    try:
        new_state = sm.transition("RESOLVED")
    except Exception as e:
        return {"error": str(e)}

    cursor.execute(
        "UPDATE work_items SET status = %s WHERE id = %s",
        (new_state, incident_id)
    )

    return {"status": "resolved"}


# -------------------------------
# Close Incident
# -------------------------------
@app.post("/incidents/{incident_id}/close")
def close_incident(incident_id: int):
    REQUEST_COUNT.inc()

    cursor.execute(
        "SELECT status FROM work_items WHERE id = %s",
        (incident_id,)
    )
    result = cursor.fetchone()

    if not result:
        return {"error": "incident not found"}

    state = result[0]

    # Check RCA exists
    cursor.execute(
        "SELECT * FROM rca WHERE work_item_id = %s",
        (incident_id,)
    )
    rca = cursor.fetchone()

    sm = WorkItemStateMachine(state)

    try:
        new_state = sm.transition("CLOSED", has_rca=bool(rca))
    except Exception as e:
        return {"error": str(e)}

    cursor.execute(
        "UPDATE work_items SET status = %s WHERE id = %s",
        (new_state, incident_id)
    )

    return {"status": "closed"}


# -------------------------------
# Metrics Endpoint
# -------------------------------
@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type="text/plain")