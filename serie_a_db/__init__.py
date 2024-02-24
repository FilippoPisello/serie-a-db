from pathlib import Path

MODULE_DIR = Path(__file__).parent.resolve()
QUERIES_DIR = MODULE_DIR / "queries"
DEFINITIONS_DIR = QUERIES_DIR / "definitions"

PROJECT_DIR = MODULE_DIR.parent.resolve()
DB_DIR = PROJECT_DIR / "db"
