"""Export views to CSVs."""

from pathlib import Path

from serie_a_db import EXPORTS_DIR, VIEWS_DIR
from serie_a_db.db.client import Db


def export_views_to_csv(db: Db) -> None:
    """Run all the queries in the views folder and save their results to CSVs."""
    for query in VIEWS_DIR.iterdir():
        result = db.select(query.read_text(), include_attributes=True)
        _result_to_csv(result, EXPORTS_DIR / (query.stem + ".csv"))


def _result_to_csv(result: list[tuple], file_path: Path) -> None:
    """Write the result to a CSV file."""
    with file_path.open("w") as file:
        for row in result:
            file.write(",".join(map(str, row)) + "\n")
