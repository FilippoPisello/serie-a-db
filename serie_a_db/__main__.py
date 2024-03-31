"""Module entry point."""

from argparse import ArgumentParser, Namespace

from serie_a_db.db.build import create_meta_tables
from serie_a_db.db.db import Db
from serie_a_db.update.db_update import update_db


def main() -> None:
    """Run the Serie A database."""
    args = _parse_args()

    db = Db()

    if args.update:
        create_meta_tables(db)
        update_db(db)


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
