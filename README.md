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
