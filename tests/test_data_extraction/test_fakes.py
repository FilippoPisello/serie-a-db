"""Test that fake objects can be created."""

from serie_a_db.data_extraction.table_specific_extractors.st_match import Match
from serie_a_db.data_extraction.table_specific_extractors.st_match_day import MatchDay


def test_fake_match_day():
    MatchDay.fake()


def test_fake_st_match():
    Match.fake()
