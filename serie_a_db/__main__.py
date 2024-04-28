"""Module entry point."""

from argparse import ArgumentParser, Namespace

from serie_a_db.db.client import Db
from serie_a_db.db.schema import TABLES
from serie_a_db.db.update import DbUpdater


def main() -> None:
    """Run the Serie A database."""
    args = _parse_args()

    db = Db()

    if args.update:
        db.meta.create_meta_tables()
        builder = DbUpdater(db, schema=TABLES)
        builder.update_all_tables()
        db.close_connection()


def _parse_args() -> Namespace:
    parser = ArgumentParser(prog="serie_a_db", description="Serie A database")
    parser.add_argument(
        "--update",
        action="store_true",
        default=False,
        help="Update all the tables in the database.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
