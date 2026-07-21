# Blue Lock Analytics

A real-time IoT telemetry ingestion and anomaly-detection platform.
Devices stream metrics (temperature, RPM, vibration) over WebSocket;
the backend scores each reading against a healthy baseline using a
vector-distance calculation, stores it, and exposes rolled-up
analytics (hourly summaries, daily exposure, a critical-risk
watchlist) through a REST API. A small React dashboard reads that API.

## Architecture

```
[ simulated / real devices ]
         |  WebSocket (JSON telemetry)
         v
[ FastAPI gateway  (app/main.py) ]
    - validates payload shape (pydantic)
    - scores drift from baseline (app/math_engine.py)
    - persists frame (app/storage.py -> SQLite)
    - serves analytics views over REST
         |
         v
[ scripts/aggregate_hourly.py ]  -> rolls raw rows into hourly/daily summary tables
[ ml/train_anomaly_detector.py ] -> trains an Isolation Forest on historical drift values
         |
         v
[ frontend/ (React + Vite) ] -> reads /api/analytics/watchlist etc.
```

## Running locally

Backend:
```
pip install -r requirements.txt
uvicorn app.main:app --reload
```
This starts the API at `http://127.0.0.1:8000` and creates `telemetry_grid.db`
in the working directory (schema applied automatically on startup).

Generate some traffic (either or both):
```
python -m scripts.simulate_client        # live simulated devices
python -m scripts.generate_mock_data --rows 50000   # bulk historical data
```

Roll raw telemetry into hourly/daily summaries (needed before the
watchlist endpoints return anything):
```
python -m scripts.aggregate_hourly
```

Train the anomaly detector:
```
python -m ml.train_anomaly_detector
```

Run tests:
```
pytest
```

### Authentication

Two separate auth mechanisms, because devices and dashboard users
aren't the same kind of caller:

- **Dashboard (analytics endpoints, `/api/analytics/*`)** — JWT login.
  Create an account, then log in to get a token:
  ```
  python -m scripts.create_user
  ```
  `POST /api/auth/login` (form-encoded `username`/`password`) returns
  `{"access_token": "...", "token_type": "bearer"}`. Send it as
  `Authorization: Bearer <token>` on analytics requests.

- **Devices (telemetry ingestion, `/api/v1/telemetry` and the
  WebSocket)** — a shared API key, not a login. Set `DEVICE_API_KEY`
  as an environment variable on both the server and any client
  (`scripts/simulate_client.py` reads the same variable). Devices
  send it as the `x-api-key` header.

Both auth secrets (`JWT_SECRET_KEY`, `DEVICE_API_KEY`) fall back to
insecure dev defaults if unset — **set real values before deploying
anywhere public.**

Frontend:
```
cd frontend
npm install
npm run dev
```
Open the printed local URL (usually `http://localhost:5173`).

## Project layout

- `app/` — the FastAPI service: gateway, scoring logic, storage, schema.
- `scripts/` — one-off/periodic jobs (device simulator, mock data generator, aggregator).
- `ml/` — model training, separate from the live request path.
- `tests/` — pytest suite for the scoring logic and storage layer.
- `frontend/` — React + Vite dashboard.

## Status / next steps

Done: one backend framework, no placeholder modules, tests for the
logic that matters, idempotent schema migrations, JWT auth for the
dashboard + API-key auth for devices.

Not yet done (next passes): CI (run tests on every push), a real
deployment target, rate limiting on the login endpoint, and honest
versions of the deep-learning/GenAI pieces once there's a real use
case for them.
