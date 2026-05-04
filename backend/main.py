from fastapi import FastAPI
import asyncio

app = FastAPI()

from datetime import datetime, timedelta

# Track recent signals per component
recent_signals = {}

# Store active incidents
active_incidents = {}

# Create queue
signal_queue = asyncio.Queue()

# API to receive signals
@app.post("/signals")
async def ingest_signal(signal: dict):
    await signal_queue.put(signal)
    return {"status": "queued"}

# Worker to process signals
#async def worker():
#    while True:
#        signal = await signal_queue.get()
#        print("Processing signal:", signal)
#        signal_queue.task_done()
async def worker():
    while True:
        signal = await signal_queue.get()

        component = signal.get("component_id")
        now = datetime.utcnow()

        # Initialize if not exists
        if component not in recent_signals:
            recent_signals[component] = []

        # Add current timestamp
        recent_signals[component].append(now)

        # Remove old signals (>10 sec)
        recent_signals[component] = [
            t for t in recent_signals[component]
            if now - t < timedelta(seconds=10)
        ]

        # Check if incident already exists
        if component in active_incidents:
            incident_id = active_incidents[component]
            print(f"Linking signal to existing incident {incident_id}")
        else:
            # Create new incident
            incident_id = len(active_incidents) + 1
            active_incidents[component] = incident_id
            print(f"Created NEW incident {incident_id} for {component}")

        signal_queue.task_done()

# Start worker on app startup
@app.on_event("startup")
async def start_worker():
    asyncio.create_task(worker())

@app.get("/")
async def root():
    return {"message": "IMS system running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
