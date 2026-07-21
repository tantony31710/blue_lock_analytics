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

## Deploying (Vercel + Supabase)

Two separate Vercel projects — don't try to combine them, that's what
caused config errors originally:

**Backend** (repo root):
1. Vercel → New Project → import this repo → **Root Directory: `.`**
2. Framework preset: FastAPI (auto-detected via `app/main.py`)
3. Environment variables:
   - `DATABASE_URL` — your Supabase connection string. Use the
     **connection pooler** (port 6543, transaction mode), not the
     direct connection — serverless functions open many short-lived
     connections and the pooler is built for that. Find it in
     Supabase → Project Settings → Database → Connection string.
   - `JWT_SECRET_KEY`, `DEVICE_API_KEY` — the same random values you generated for local use
   - `ALLOWED_ORIGINS` — your frontend's Vercel URL once you have it (comma-separated if more than one)
4. Deploy.

**Frontend** (separate project):
1. Vercel → New Project → import the same repo → **Root Directory: `frontend`**
2. Framework preset: Vite (auto-detected)
3. Environment variable: `VITE_API_BASE` = your backend's Vercel URL
4. Deploy.

Then go back to the backend project's `ALLOWED_ORIGINS` and set it to
the frontend URL you just got, redeploy the backend.

**Known limits of this setup**: WebSocket support on Vercel is in
public beta — connections auto-close after `maxDuration` (60s here)
and the client reconnects (already handled in `scripts/simulate_client.py`
and would need the same in any real device firmware). State isn't
shared between function instances, which is exactly why this migrated
to Postgres instead of relying on SQLite.

## Status / next steps

Done: one backend framework, no placeholder modules, tests for the
logic that matters, idempotent schema migrations, JWT auth for the
dashboard + API-key auth for devices, CI, Postgres-backed production
deploy on Vercel + Supabase.

Not yet done: Row Level Security policies on the Supabase tables
(currently off — safe today since only the backend connects directly,
but worth adding as defense-in-depth), rate limiting on the login
endpoint, and honest versions of the deep-learning/GenAI pieces once
there's a real use case for them.
