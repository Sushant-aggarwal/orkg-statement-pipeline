"""Test for the dlt pipeline.

What it checks:
- Pipeline runs without error (extract → load)
- Rows land in the destination table (exact count 2)

Why this is enough now:
- It proves the wiring works end-to-end with dlt + destination.
- Keeps the test simple and stable (one mocked page, no pagination edge cases).
"""

from pathlib import Path
import dlt
import duckdb
import pytest

# Import your actual source (adjust the path/name if different)
import backend.pipeline.source_statement as src_mod


class _MockResp:
    """Tiny Response stand-in with just what's needed."""
    def __init__(self, payload, status_code=200, url="http://fake/api"):
        self._payload = payload
        self.status_code = status_code
        self.ok = status_code == 200
        self.url = url
        self.headers = {}

    def json(self):
        return self._payload

    def raise_for_status(self):
        if not self.ok:
            raise RuntimeError(f"HTTP {self.status_code} for {self.url}")


def test_pipeline_smoke(monkeypatch, tmp_path: Path):
    # --- Arrange: mock ORKG API with a single page of two records ---
    def fake_get(url, params=None, timeout=None):
        payload = {
            "content": [
                {"id": "P1", "title": "Paper A", "count": 7},
                {"id": "P2", "title": "Paper B", "count": 3},
            ],
            "page": {"size": 2, "total_elements": 2, "total_pages": 1, "number": 0},
        }
        return _MockResp(payload)

    monkeypatch.setattr(src_mod.requests, "get", fake_get, raising=True)

    # Put dlt state/db under tmp so the test is isolated
    duck_path = tmp_path / "smoke.duckdb"
    monkeypatch.setenv("DLT_PIPELINE_DIR", str(tmp_path))
    monkeypatch.setenv("DESTINATION__DUCKDB__CREDENTIALS__DATABASE", str(duck_path))

    # --- Act: run the real pipeline into DuckDB ---
    pipe = dlt.pipeline(
        pipeline_name="smoke_pipeline",
        destination="duckdb",
        dataset_name="test_ds",
    )
    info = pipe.run(src_mod.statement_source())

    # --- Assert: load happened and exactly two rows exist ---
    assert info is not None and info.loads_ids

    con = duckdb.connect(str(duck_path))
    # Adjust table name if your resource name differs from "papers_statement_counts"
    total = con.execute(
        "SELECT COUNT(*) FROM test_ds.papers_statement_counts"
    ).fetchone()[0]
    assert total == 2