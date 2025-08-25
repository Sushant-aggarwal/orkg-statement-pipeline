from typing import Iterator, List, Dict, Any, Optional
import dlt, requests

API = "https://orkg.org/api/papers/statement-counts"

@dlt.source
def statement_source(page_size: int = 2500, title_filter: Optional[str] = None):

    @dlt.resource(
        name="papers_statement_counts",
        primary_key="id",
        write_disposition="merge",
    )
    def papers_statement_counts() -> Iterator[List[Dict[str, Any]]]:
        page = 0
        while True:
            params = {"size": page_size, "page": page}
            if title_filter:
                params["title"] = title_filter

            r = requests.get(API, params=params, timeout=60)
            r.raise_for_status()
            data = r.json()

            content = data.get("content", [])
            if content:
                yield [
                    {
                        "id": row.get("id"),
                        "title": row.get("title") or row.get("id"),
                        "count": int(row.get("count", 0)),
                    }
                    for row in content
                ]

            meta = data.get("page") or {}
            total_pages = meta.get("total_pages")

            if total_pages is not None and page >= total_pages:
                break
            if total_pages is None and len(content) < page_size:
                break
            page += 1

    return papers_statement_counts