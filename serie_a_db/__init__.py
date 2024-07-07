"""Module for Serie A database."""

from pathlib import Path

MODULE_DIR = Path(__file__).parent.resolve()
CONFIG_FILE = MODULE_DIR / "config.yml"

QUERIES_DIR = MODULE_DIR / "queries"
DEFINITIONS_DIR = QUERIES_DIR / "definitions"
META_DIR = QUERIES_DIR / "meta"

PROJECT_DIR = MODULE_DIR.parent.resolve()
DB_FILE = PROJECT_DIR / "serie_a.db"
