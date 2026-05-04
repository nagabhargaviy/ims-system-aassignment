from fastapi import FastAPI, Request
from kafka import KafkaProducer
import json

app = FastAPI()

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/signals")
async def ingest_signal(request: Request):
    data = await request.json()
    producer.send("signals", data)
    return {"status": "queued"}
