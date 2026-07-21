# Blue Lock Analytics Platform

## Project Overview

The Blue Lock Analytics Platform is a professional-grade telemetry ingestion and anomaly detection system designed to monitor critical device metrics in real-time. It processes high-frequency data streams, calculates vector drift against healthy baselines, and identifies critical anomalies, providing immediate insights into system health. This platform is built with a focus on scalability, maintainability, and robust data processing, moving beyond typical student projects to a production-ready architecture.

## Architecture Diagram

```
+-----------------------+
|     Device Telemetry  |
| (Sensors, IoT, etc.)  |
+-----------+-----------+
            |
            | WebSocket / REST (FastAPI)
            V
+-----------------------+
|   Telemetry Gateway   |
|    (telemetry_gateway)|
|                       |
| - Ingests raw data    |
| - Calculates drift    |
| - Persists to DB      |
+-----------+-----------+
            |
            | SQLite (telemetry_grid.db)
            V
+-----------------------+
|    Data Engineering   |
|    (data_engineering) |
|                       |
| - Manages DB schema   |
| - Handles data storage|
+-----------+-----------+
            |
            | Queries
            V
+-----------------------+
|        Analytics      |
|       (analytics)     |
|                       |
| - Provides watchlist  |
| - Optimized indexing  |
+-----------+-----------+
            |
            | Model Training
            V
+-----------------------+
|           ML          |
|         (ml)          |
|                       |
| - Anomaly Detection   |
| - Isolation Forest    |
+-----------+-----------+
            |
            | Frontend API Calls
            V
+-----------------------+
|       Frontend        |
|      (frontend)       |
|                       |
| - React Dashboard     |
| - Real-time display   |
+-----------------------+
```

## Getting Started

Follow these instructions to set up and run the Blue Lock Analytics Platform locally.

### Prerequisites

- Python 3.9+
- Node.js (for frontend)
- npm or yarn (for frontend)

### Backend Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/tantony31710/blue_lock_analytics.git
    cd blue_lock_analytics
    ```

2.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Initialize the database schema:**
    ```bash
    python -c "from data_engineering.advanced_sql.storage_manager import StorageManager; sm = StorageManager(); sm.initialize_schema(sql_script_path=\'data_engineering/advanced_sql/migrate.sql\')"
    ```

4.  **Train the ML model (optional, but recommended for full functionality):**
    ```bash
    python ml/train_anomaly_detector.py
    ```

5.  **Run the FastAPI backend:**
    ```bash
    uvicorn telemetry_gateway.API:app --reload --host 0.0.0.0 --port 8000
    ```
    The API will be accessible at `http://0.0.0.0:8000`.

### Frontend Setup

1.  **Navigate to the frontend directory:**
    ```bash
    cd frontend
    ```

2.  **Install Node.js dependencies:**
    ```bash
    npm install
    ```

3.  **Run the React development server:**
    ```bash
    npm run dev
    ```
    The frontend application will typically open in your browser at `http://localhost:5173` (or another available port).

## Running Tests

To ensure the integrity of the codebase, run the provided unit tests:

```bash
pytest tests/
```

## CI/CD

This project includes a GitHub Actions workflow (`.github/workflows/ci.yml`) that automatically runs tests on every push to the `main` branch and on pull requests. This ensures code quality and helps prevent regressions.

## Future Enhancements

-   **Authentication & Input Hardening:** Implement robust authentication for API endpoints and harden input validation to prevent malicious data injection.
-   **Real Deployment:** Deploy the FastAPI backend and React frontend to a cloud platform (e.g., Render, Railway, Vercel) for public accessibility.
-   **Advanced Analytics:** Integrate more sophisticated analytical models and visualizations.
-   **Real-time Dashboard:** Enhance the frontend with real-time data updates and interactive charts.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
