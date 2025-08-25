import math
from typing import Optional, List, Any
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from .db import get_conn

TABLE = "scikgdash_stmt.papers_statement_counts"

app = FastAPI(title="scikgdash statements backend")

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health():
    return {"ok": True}

@app.get("/api/statements")
def get_statements(
    page: int = Query(0, ge=0),
    size: int = Query(50, ge=1, le=5000),
    title: Optional[str] = Query(None),
):
    offset = page * size
    where = ""
    params: List[Any] = []
    if title:
        where = "WHERE title ILIKE %s"
        params.append(f"%{title}%")

    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(f"SELECT COUNT(*) FROM {TABLE} {where}", params)
        total_elements = cur.fetchone()[0]
        total_pages = math.ceil(total_elements / size) if total_elements else 0

        cur.execute(
            f"""
            SELECT id, title, count
            FROM {TABLE}
            {where}
            ORDER BY count DESC, id
            LIMIT %s OFFSET %s
            """,
            params + [size, offset],
        )
        rows = [
            {"id": r[0], "title": r[1], "count": int(r[2])}
            for r in cur.fetchall()
        ]

    return {
        "content": rows,
        "page": {
            "size": size,
            "total_elements": total_elements,
            "total_pages": total_pages,
            "number": page,
        },
    }