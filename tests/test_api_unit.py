from fastapi.testclient import TestClient
import types

from backend.app.main import app
import backend.app.main as main_mod


class _FakeCursor:
    def __init__(self, rows, count=0):
        self._rows = rows
        self._count = count
        self.last_sql = None
        self.last_params = None

    def execute(self, sql, params=None):
        self.last_sql = sql
        self.last_params = params or []

    def fetchone(self):
        # total count (for pagination)
        return (self._count,)

    def fetchall(self):
        # rows for page
        return self._rows

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class _FakeConn:
    def __init__(self, rows, count):
        self._rows = rows
        self._count = count

    def cursor(self):
        return _FakeCursor(self._rows, self._count)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


def test_statements_endpoint_paginates_and_filters(monkeypatch):
    """Unit-level test: API returns expected shape & pagination without a real DB."""
    # prepare fake data: 3 rows total; first page returns 2
    fake_all_rows = [
        ("P1", "Paper One", 10),
        ("P2", "Paper Two", 5),
        ("P3", "Paper Three", 1),
    ]
    page0_rows = fake_all_rows[:2]
    total_count = len(fake_all_rows)

    def fake_get_conn():
        return _FakeConn(page0_rows, total_count)

    monkeypatch.setattr(main_mod, "get_conn", fake_get_conn, raising=True)

    client = TestClient(app)
    resp = client.get("/api/statements?page=0&size=2&title=paper")
    assert resp.status_code == 200
    body = resp.json()

    # response shape checks
    assert "content" in body and "page" in body
    assert isinstance(body["content"], list)
    assert len(body["content"]) == 2
    assert {"id", "title", "count"} <= set(body["content"][0].keys())

    # pagination metadata
    page_meta = body["page"]
    assert page_meta["size"] == 2
    assert page_meta["number"] == 0
    assert page_meta["total_elements"] == total_count
    assert page_meta["total_pages"] == 2  # ceil(3/2) = 2

    # rows ordering (as your API sorts by count DESC, id)
    assert body["content"][0]["id"] == "P1"
    assert body["content"][0]["count"] == 10