from serie_a_db.data_extraction.clients.fantacalcio_punto_it_website import (
    FantacalcioPuntoItWebsite,
)
from serie_a_db.data_extraction.table_specific_extractors.shared_definitions import (
    PlayerRole,
)
from serie_a_db.data_extraction.table_specific_extractors.st_fpi_player import (
    FpiPlayer,
    parse_players_page,
)
from tests.conftest import DEFAULT_FROZEN_TIME
from tests.test_data_extraction import EXTRACTION_TEST_DATA_DIR

A_SEASON_ID = "2023"


def test_player_parsing_with_one_player(freeze_time):
    # Arrange
    page = EXTRACTION_TEST_DATA_DIR / "fpi/player_one_player.html"

    # Act
    data = parse_players_page(page.read_text(), A_SEASON_ID)

    # Assert
    assert data == [
        FpiPlayer(
            season_id=A_SEASON_ID,
            load_ts=DEFAULT_FROZEN_TIME.isoformat(sep=" ", timespec="milliseconds"),
            team_id="INT",
            name="Martinez L.",
            code_fpi=2764,
            role=PlayerRole.ATTACKER,
            price_initial=41,
            price_current=41,
        ).to_namedtuple()
    ]


class TestCodeExtractionFromUrl:
    BASE_URL = "https://www.fantacalcio.it/serie-a/squadre/inter"
    ID = 2764

    def test_season_in_the_url_should_be_ignored(self):
        url = self.BASE_URL + f"/{self.ID}/2023-24"
        assert FantacalcioPuntoItWebsite.strip_player_id_from_url(url) == self.ID

    def test_code_as_the_last_part_should_be_extracted(self):
        url = self.BASE_URL + f"/{self.ID}"
        assert FantacalcioPuntoItWebsite.strip_player_id_from_url(url) == self.ID
