# Sentinel‑Scope

## Project Purpose
Sentinel‑Scope is a lightweight, modular web‑traffic monitoring dashboard that aggregates reverse‑proxy logs, detects anomalous user‑agent patterns, and visualizes potential bot or ARG activity—all running locally with no external paid APIs. It helps security teams quickly spot suspicious traffic and investigate potential automated attacks.

## Prerequisites
- Python 3.9 or newer
- pip (Python package installer)

## Installation
```bash
# 1. Clone the repository
git clone https://github.com/yourorg/sentinel-scope.git
cd sentinel-scope

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

## Ingesting Logs
Logs are ingested via the `/ingest` endpoint. The payload must be JSON and include the required fields: `timestamp`, `remote_addr`, `request_method`, `request_uri`, `status_code`, `user_agent`.

```bash
curl -X POST http://localhost:8000/ingest \
     -H "Content-Type: application/json" \
     -d '{
           "timestamp": "2024-06-18T12:34:56Z",
           "remote_addr": "192.0.2.1",
           "request_method": "GET",
           "request_uri": "/api/v1/resource",
           "status_code": 200,
           "user_agent": "Mozilla/5.0 (compatible; Bot/1.0)"
         }'
```

## Starting the Server
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```
The API will be available at `http://localhost:8000`. The ingestion endpoint is `/ingest`, and the dashboard is served at `/dashboard`.

## Dashboard URL
Once the server is running, open your browser and navigate to:
```
http://localhost:8000/dashboard
```
You will see real‑time charts of request volume, user‑agent distribution, and anomaly alerts.

## How it Works
1. **Log Collection** – Reverse‑proxy logs are forwarded to Sentinel‑Scope via HTTP POST. Each log entry is parsed and stored in an in‑memory SQLite database.
2. **Feature Extraction** – Every log is processed to extract features such as request frequency, user‑agent fingerprint, and response status.
3. **Anomaly Detection** – A lightweight statistical model (z‑score on request rate and user‑agent entropy) flags traffic that deviates from the baseline. Suspicious entries are marked in the database.
4. **Visualization** – The FastAPI dashboard uses Plotly Dash to render interactive graphs. It queries the database every few seconds to refresh the charts, highlighting anomalous points in red.
5. **Alerting** – Optionally, a background task can send email or Slack notifications for high‑severity anomalies (configurable in `config.yaml`).

## Troubleshooting
| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| `ModuleNotFoundError: No module named 'uvicorn'` | Uvicorn not installed | `pip install uvicorn` |
| `ERROR: Could not parse JSON` | Malformed log payload | Validate JSON with `jq` or ensure all required fields are present |
| `Database locked` | Concurrent writes to SQLite | Reduce ingestion rate or switch to a more robust DB (PostgreSQL) |
| Dashboard shows no data | Ingestion endpoint not hit | Verify logs are being POSTed to `/ingest` and check server logs |
| `Connection refused` | Server not running | Start the server with `uvicorn` or check firewall rules |

For additional help, consult the issue tracker or open a new issue on GitHub.