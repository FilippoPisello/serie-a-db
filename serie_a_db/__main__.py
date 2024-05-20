"""Module entry point."""

import logging
import sys
from argparse import ArgumentParser, Namespace

from serie_a_db import CONFIG_FILE
from serie_a_db.db.client import Db
from serie_a_db.db.schema import TABLES
from serie_a_db.db.update import DbUpdater
from serie_a_db.utils import read_yaml

LOGGER = logging.getLogger(__name__)


def main() -> None:
    """Run the Serie A database."""
    _setup_logging()
    args = _parse_args()

    db = Db()

    if args.update:
        LOGGER.info("Updating all tables in the database...")
        db.meta.create_meta_tables()
        db.meta.set_parameters(read_yaml(CONFIG_FILE)["parameters"])
        builder = DbUpdater(db, schema=TABLES)
        builder.update_all_tables()
        db.close_connection()
        LOGGER.info("Update completed!")


def _parse_args() -> Namespace:
    parser = ArgumentParser(prog="serie_a_db", description="Serie A database")
    parser.add_argument(
        "--update",
        action="store_true",
        default=False,
        help="Update all the tables in the database.",
    )
    return parser.parse_args()


def _setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout,
    )


if __name__ == "__main__":
    main()
