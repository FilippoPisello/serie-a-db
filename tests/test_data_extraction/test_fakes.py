"""Test that fake objects can be created."""

from serie_a_db.data_extraction.table_specific_extractors.dm_match_day import MatchDay
from serie_a_db.data_extraction.table_specific_extractors.st_match import Match


def test_fake_match_day():
    MatchDay.fake()


def test_fake_st_match():
    Match.fake()
