"""Functions useful for testing."""

import pytest

from serie_a_db.utils import strip_whitespaces_and_newlines


def strings_equivalent(str1: str, str2: str) -> bool:
    """Check if strings are equal after removing newlines and multiple spaces."""
    parsed_str1 = strip_whitespaces_and_newlines(str1)
    parsed_str2 = strip_whitespaces_and_newlines(str2)
    return parsed_str1 == parsed_str2


@pytest.mark.parametrize(
    ("string1", "string2"),
    [
        ("lorem ipsum", "lorem  ipsum"),
        ("lorem ipsum", "lorem      ipsum"),
        ("lorem ipsum", "lorem ipsum"),
        ("lorem ipsum", "lorem\nipsum"),
    ],
)
def test_strings_equivalent(string1, string2):
    assert strings_equivalent(string1, string2)
