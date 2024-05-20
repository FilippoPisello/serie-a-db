"""Test that fake objects can be created."""

from serie_a_db.data_extraction.table_specific_extractors.dm_match_day import MatchDay


def test_fake_match_day():
    MatchDay.fake()
