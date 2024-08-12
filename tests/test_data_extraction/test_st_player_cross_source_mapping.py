import pytest

from serie_a_db.data_extraction.table_specific_extractors.shared_definitions import (
    PlayerRole,
)
from serie_a_db.data_extraction.table_specific_extractors.st_player_cross_source_mapping import (
    PlayerMapping,
    PlayerRecord,
    find_player_mappings,
)


class TestMappings:

    def test_two_identical_players_shuold_be_matched(self):
        pl1 = pl2 = PlayerRecord.fake(code=1)

        actual = find_player_mappings({"JUV": {pl1}}, {"JUV": {pl2}}, "S2023")

        assert actual == [
            PlayerMapping(season_id="S2023", code_fpi=1, code_fm=1).to_namedtuple()
        ]

    def test_two_players_sharing_name_and_team_shuold_be_matched(self):
        pl1 = PlayerRecord(code=1, name="Foo", role=PlayerRole.ATTACKER)
        pl2 = PlayerRecord(code=1, name="Foo", role=PlayerRole.DEFENDER)

        actual = find_player_mappings({"JUV": {pl1}}, {"JUV": {pl2}}, "S2023")

        assert actual == [
            PlayerMapping(season_id="S2023", code_fpi=1, code_fm=1).to_namedtuple()
        ]

    def test_full_match_should_take_precedence_over_partial_match(self):
        pl1 = PlayerRecord(code=1, name="Foo", role=PlayerRole.ATTACKER)
        pl2 = PlayerRecord(code=1, name="Foo", role=PlayerRole.DEFENDER)
        pl3 = PlayerRecord(code=2, name="Foo", role=PlayerRole.ATTACKER)

        actual = find_player_mappings({"JUV": {pl2, pl3}}, {"JUV": {pl1}}, "S2023")

        assert actual == [
            PlayerMapping(season_id="S2023", code_fpi=2, code_fm=1).to_namedtuple()
        ]

    def test_players_with_similar_enough_names_should_be_matched(self):
        pl1 = PlayerRecord.fake(code=1, name="Vlahovic")
        pl2 = PlayerRecord.fake(code=1, name="Vlahovic D.")

        actual = find_player_mappings({"JUV": {pl1}}, {"JUV": {pl2}}, "S2023")

        assert actual == [
            PlayerMapping(season_id="S2023", code_fpi=1, code_fm=1).to_namedtuple()
        ]

    def test_fm_player_without_a_match_should_result_in_error(self):
        with pytest.raises(ValueError):
            find_player_mappings(
                {"JUV": set()}, {"JUV": {PlayerRecord.fake()}}, "S2023"
            )


def test_lorem():
    from serie_a_db.db.client import Db
    from serie_a_db.db.schema import TABLES
    from serie_a_db.db.update import DbUpdater

    db = Db()
    updated = DbUpdater(db, TABLES)
    updated.update_table_and_upstream_dependencies(
        TABLES["st_player_cross_source_mapping"]
    )
