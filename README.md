                    +----------------------+
                    |   Client / Services  |
                    +----------+-----------+
                               |
                          (Ingress)
                               |
                    +----------v-----------+
                    |  FastAPI Ingestion   |
                    |  - Rate Limit        |
                    |  - Validation        |
                    +----------+-----------+
                               |
                          (Async Push)
                               |
                        +------v------+
                        |   Kafka     |
                        |  (signals)  |
                        +------+------+
                               |
                    +----------v-----------+
                    |  Consumer Workers   |
                    |  - Debounce (Redis) |
                    |  - Processing       |
                    +----+----+----+------+
                         |    |    |
          +--------------+    |    +----------------+
          |                   |                     |
+---------v--------+  +-------v-------+   +---------v--------+
|     Redis        |  |  PostgreSQL   |   |       S3         |
| (Hot Cache +     |  | (Source of    |   | (Raw Signals)    |
|  Debounce Keys)  |  |  Truth)       |   |                  |
+------------------+  +---------------+   +------------------+
                              |
                      +-------v--------+
                      |   Query API    |
                      +-------+--------+
                              |
                        +-----v------+
                        |  Frontend  |
                        +------------+

Observability:
Prometheus → metrics
Grafana → dashboards
Alertmanager → alerts


# Incident Management System (IMS)

## Architecture

FastAPI → Kafka → Consumer → Redis (debounce) → Postgres → Metrics

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