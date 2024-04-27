"""Useful support functions."""

import datetime
import re


def strip_whitespaces_and_newlines(string: str) -> str:
    """Turn consecutive spaces into one and remove newlines."""
    return " ".join(string.split()).replace("\n", "")


def split_no_empty(string: str, sep: str, maxplit: int = -1) -> list[str]:
    """Split a string and remove empty strings."""
    return [
        bit.strip()
        for bit in string.split(sep, maxplit)
        if strip_whitespaces_and_newlines(bit)
    ]


def from_camel_to_snake_case(name: str) -> str:
    """Convert a camel case string to snake case."""
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


FREEZE_TIME_TO = None


def now() -> datetime.datetime:
    """Return the current date and time.

    Redefining this function to allow for time freezing in tests.
    """
    if FREEZE_TIME_TO:
        return FREEZE_TIME_TO
    return datetime.datetime.now()
