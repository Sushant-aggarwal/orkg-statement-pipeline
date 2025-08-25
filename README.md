# ORKG Statement Counts — dlt → Postgres → FastAPI → React (Histogram)

## What we’re doing (and why)

We’re building a pipeline + API + UI for analyzing **statements per paper** in the [ORKG](https://orkg.org).

- **Extract** “statements per paper” data from the ORKG API.  
- **Load** it into **Postgres** using [dlt](https://dlthub.com).  
- **Serve** it via a **FastAPI** backend.  
- **Visualize** it in a simple **React (Vite)** frontend as a histogram.  

### Why use dlt?
- **Idempotent loads** — define a `primary_key` and `merge` mode so data is safely updated on re-run.  
- **Pagination handled** — ORKG’s API is paged; dlt can stream this easily.  
- **Schema management** — dlt infers or enforces schema in Postgres.  
- **Reproducible** — config + secrets separated, easy to share or schedule.  

---

## Prerequisites

Make sure you have the following installed:

- **Python** 3.10+  
- **Node.js** 18+  
- **Postgres** 13+ (running on `localhost:5432`)  

And in Postgres, create the database:

```sql
-- Database
CREATE DATABASE orkgstatement;
```
## Installation & Setup

Follow these steps to set up the project locally.


### clone repo and enter project folder
```
git clone <repo-url>
cd orkg-statement-pipeline
```

### create virtualenv
```
python -m venv dlt-env
source dlt-env/bin/activate   # on Windows use: dlt-env\Scripts\activate
```

### install dependencies (backend)
```
pip install -r requirement.txt
```

### install dependencies (frontend)
```
cd frontend
npm install
```

### run the dlt pipeline (loads ORKG data into Postgres)
```
python -m backend.pipeline.run
```

### start FastAPI server
```
uvicorn backend.app.main:app --reload --port 8000
```
### start frontend
```
npm run dev
```
## Environment Variables

Set up the following environment files before running the project:

### .env (repo root, **not committed**)  
Used by **FastAPI / psycopg2** for Postgres connection:

```
PGHOST=localhost
PGPORT=5432
PGDATABASE=orkgstatement
PGUSER=user
PGPASSWORD=password
```

### .dlt/secrets.toml (**not committed**)  
Used by **dlt pipeline** to connect to Postgres (reuses the same env vars):

```toml
[destination.postgres.credentials]
host = "${PGHOST}"
port = "${PGPORT}"
database = "${PGDATABASE}"
username = "${PGUSER}"
password = "${PGPASSWORD}"
```

### frontend/.env  

```
VITE_API_BASE=http://localhost:8000
```

## Future Plans

### 1) Scheduled refresh (cron)
We’ll refresh the dataset automatically with a cron job. This runs the dlt pipeline on a schedule and upserts new/changed rows into Postgres.

### 2) Use dlt incremental loads where timestamps exist
The ORKG “statements per paper” endpoint doesn’t expose created_at / updated_at, so we currently do a full fetch and merge on id.
However, other ORKG APIs do provide timestamps. For those, we’ll switch to a true incremental pattern so each run only fetches rows updated since the last sync.

## Tests

This project includes two main kinds of tests:

1. **Unit Test (API)**
   - `tests/test_api_unit.py`
   - Uses a **fake DB connection** (no Postgres needed).
   - Verifies that `/api/statements` returns the correct response shape, pagination metadata, and ordering.

2. **Pipeline Test (dlt)**
   - `tests/test_pipeline_smoke.py`
   - Uses **DuckDB** and a **mocked ORKG API** response.
   - Verifies that the dlt pipeline runs end-to-end, loads rows without error, and writes them to the destination table.
### Run Tests
```
pytest -v
```
---


