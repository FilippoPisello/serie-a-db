"""Useful support functions."""


def strip_whitespaces_and_newlines(string: str) -> str:
    """Turn consecutive spaces into one and remove newlines."""
    return " ".join(string.split()).replace("\n", "")


def split_no_empty(string: str, sep: str, maxplit: int = -1) -> list[str]:
    """Split a string and remove empty strings."""
    return [
        bit for bit in string.split(sep, maxplit) if strip_whitespaces_and_newlines(bit)
    ]
