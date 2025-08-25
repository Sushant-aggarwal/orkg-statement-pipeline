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
pip install -r requirements.txt
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

