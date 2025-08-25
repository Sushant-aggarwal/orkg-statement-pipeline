import dlt
from .source_statement import statement_source

def run(page_size: int = 2500, title_filter: str | None = None):
    pipe = dlt.pipeline(
        pipeline_name="scikgdash_statement_pipeline",
        destination="postgres",
        dataset_name="orkg_stmt",
    )
    src = statement_source(page_size=page_size, title_filter=title_filter)
    print("DLT resources in source:", list(src.resources.keys()))
    info = pipe.run(src)
    print(info)
    return info

if __name__ == "__main__":
    run()