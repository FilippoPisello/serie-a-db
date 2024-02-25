"""Module entry point."""

from argparse import ArgumentParser, Namespace


def main() -> None:
    """Run the Serie A database."""
    args = _parse_args()
    print(args.update)


def _parse_args() -> Namespace:
    parser = ArgumentParser(prog="serie_a_db", description="Serie A database")
    parser.add_argument(
        "--update",
        action="extend",
        type=str,
        nargs="+",
        help="Update one or more tables of the database.",
    )
    parser.add_argument(
        "--scratch",
        action="store_true",
        default=False,
        help="Whether the tables being updated should be erased before updating.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
