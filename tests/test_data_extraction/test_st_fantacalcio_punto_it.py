from serie_a_db.data_extraction.table_specific_extractors.st_fantacalcio_punto_it import (
    PlayerMatch,
    PlayerRole,
    parse_match_day_page,
)
from tests.test_data_extraction import EXTRACTION_TEST_DATA_DIR


def test_match_day_parsing_with_one_player():
    # Arrange
    page = EXTRACTION_TEST_DATA_DIR / "fantacalcio_punto_it/one_player.html"
    a_matchday_id = "2023"

    # Act
    data = parse_match_day_page(page.read_text(), a_matchday_id)

    # Assert
    assert data == [
        PlayerMatch(
            match_day_id=a_matchday_id,
            team_name="Atalanta",
            name="Musso",
            code=2792,
            role=PlayerRole.GOALKEEPER,
            fantacalcio_punto_it_grade=6.5,
            fantacalcio_punto_it_fanta_grade=6.5,
            italia_grade=8.5,
            italia_fanta_grade=8,
            statistical_grade=7.5,
            statistical_fanta_grade=7,
            goals_scored=0,
            goals_conceded=0,
            own_goals=0,
            penalties_scored=0,
            penalties_missed=0,
            penalties_saved=0,
            assists=0,
            yellow_card=False,
            red_card=False,
            subbed_in=False,
            subbed_out=False,
        ).to_namedtuple()
    ]


def test_match_day_parsing_with_two_players_from_the_same_team():
    # Arrange
    page = EXTRACTION_TEST_DATA_DIR / "fantacalcio_punto_it/two_players_same_team.html"
    a_matchday_id = "2023"

    # Act
    data = parse_match_day_page(page.read_text(), a_matchday_id)

    # Assert
    assert len(data) == 2
    assert (
        data[1]
        == PlayerMatch(
            match_day_id=a_matchday_id,
            team_name="Atalanta",
            name="Zappacosta",
            code=554,
            role=PlayerRole.DEFENDER,
            fantacalcio_punto_it_grade=6.5,
            fantacalcio_punto_it_fanta_grade=6.5,
            italia_grade=6.5,
            italia_fanta_grade=6.5,
            statistical_grade=6.5,
            statistical_fanta_grade=6.5,
            goals_scored=1,
            goals_conceded=0,
            own_goals=0,
            penalties_scored=0,
            penalties_missed=0,
            penalties_saved=0,
            assists=0,
            yellow_card=True,
            red_card=False,
            subbed_in=False,
            subbed_out=True,
        ).to_namedtuple()
    )


def test_match_day_parsing_with_two_players_from_different_teams():
    # Arrange
    page = (
        EXTRACTION_TEST_DATA_DIR
        / "fantacalcio_punto_it/two_players_different_teams.html"
    )
    a_matchday_id = "2023"

    # Act
    data = parse_match_day_page(page.read_text(), a_matchday_id)

    # Assert
    assert len(data) == 2
    assert (
        data[1]
        == PlayerMatch(
            match_day_id=a_matchday_id,
            team_name="Bologna",
            name="Skorupski",
            code=133,
            role=PlayerRole.GOALKEEPER,
            fantacalcio_punto_it_grade=6,
            fantacalcio_punto_it_fanta_grade=4,
            italia_grade=6,
            italia_fanta_grade=4,
            statistical_grade=6,
            statistical_fanta_grade=4,
            goals_scored=0,
            goals_conceded=2,
            own_goals=0,
            penalties_scored=0,
            penalties_missed=0,
            penalties_saved=0,
            assists=0,
            yellow_card=False,
            red_card=False,
            subbed_in=False,
            subbed_out=False,
        ).to_namedtuple()
    )
