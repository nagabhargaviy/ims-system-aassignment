# Incident Management System (IMS)

## Architecture

FastAPI → Kafka → Consumer → Redis (debounce) → Postgres → Metrics

## Architecture Flow

Client → FastAPI → Kafka → Consumer → Redis (Debounce) → PostgreSQL  
                                  ↓  
                              Prometheus Metrics

## Features

- Signal ingestion via API
- Kafka-based async processing
- Debounce logic to prevent duplicate incidents
- Incident lifecycle:
  - OPEN → RESOLVED → CLOSED
- RCA enforcement before closure
- Metrics exposed via Prometheus

## How to Run

### Start Infra
docker compose up -d

### Start API
PYTHONPATH=. uvicorn backend.ingestion_api.main:app

### Start Consumer
PYTHONPATH=. python backend/consumer/worker.py

## APIs

- POST /signals
- GET /incidents
- GET /incidents/{id}
- POST /incidents/{id}/rca
- POST /incidents/{id}/resolve
- POST /incidents/{id}/close
- GET /metrics

## Notes

- Uses Redis for debounce
- PostgreSQL for persistence
- Kafka for async processing


## Example Flow

1. Send signal → POST /signals
2. Kafka queues event
3. Consumer processes:
   - Debounce via Redis
   - Creates/links incident
4. Add RCA → POST /incidents/{id}/rca
5. Resolve → POST /resolve
6. Close → POST /close