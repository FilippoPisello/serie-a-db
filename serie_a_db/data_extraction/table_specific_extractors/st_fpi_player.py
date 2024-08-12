"""Import the player list from Fantacalcio.it."""

import logging
from typing import NamedTuple

from bs4 import BeautifulSoup
from pydantic import NonNegativeInt

from serie_a_db.data_extraction.clients.fantacalcio_punto_it_website import (
    FantacalcioPuntoItWebsite,
)
from serie_a_db.data_extraction.input_base_model import DbInputBaseModel
from serie_a_db.data_extraction.table_specific_extractors.shared_definitions import (
    PlayerRole,
    log_fatal_error,
    sleep_not_to_overload_the_website,
)
from serie_a_db.data_extraction.table_specific_extractors.st_fpi_player_match import (
    translate_role,
)
from serie_a_db.db.client import Db
from serie_a_db.utils import now, strip_whitespaces_and_newlines

LOGGER = logging.getLogger(__name__)


class FpiPlayer(DbInputBaseModel):
    """A player from the player master list in Fantacalcio.it."""

    load_ts: str
    season_id: str
    team_id: str
    name: str
    code_fpi: int
    role: PlayerRole
    price_initial: NonNegativeInt
    price_current: NonNegativeInt


def scrape_player_data(
    db: Db | None = None,
    website_client: FantacalcioPuntoItWebsite | None = None,
    sleep_time: int = 30,
    max_match_days_to_scrape: int = 37,
) -> list[NamedTuple]:
    """Extract data about players performance in a match."""
    if db is None:
        db = Db()
    if website_client is None:
        website_client = FantacalcioPuntoItWebsite()

    seasons_to_import = _get_seasons_to_import(db)

    player_matches = []
    for index, (season_year_start, season_id) in enumerate(seasons_to_import, start=1):
        if index > max_match_days_to_scrape:
            _log_info_hit_max_seasons_to_scrape(max_match_days_to_scrape)
            break

        _log_info_season_being_extracted(season_id)
        match_day_results_page = website_client.get_players_list_page(season_year_start)

        # Try getting all the matches for the match day. If one fails, stop
        # without erroring out so that what successfully extracted so far
        # is still imported
        try:
            player_matches.extend(parse_players_page(match_day_results_page, season_id))
        except ValueError:
            log_fatal_error(LOGGER, season_id, "season")
            break

        sleep_not_to_overload_the_website(sleep_time)

    return player_matches


def _get_seasons_to_import(db: Db) -> list[tuple[int, str]]:
    try:
        query = """
        SELECT DISTINCT
            dms.year_start,
            dms.season_id
        FROM dm_season AS dms
            LEFT JOIN st_fpi_player AS st ON dms.season_id = st.season_id
        WHERE
            -- Either seasons with no data or non-completed seasons
            (dms.status <> 'completed'
                OR st.season_id IS NULL)
            -- Data on the website starts from season 2015/16
            AND dms.year_start >= 2015
        ORDER BY
            -- Start from the latest season
            dms.year_start DESC
        """
        return db.select(query)
    finally:
        db.close_connection()


def parse_players_page(players_page: str, season_id: str) -> list[NamedTuple]:
    """Parse the page of a match day to extract a list of player matches."""
    soup = BeautifulSoup(players_page, "html.parser")
    load_ts = now().isoformat(sep=" ", timespec="milliseconds")

    output = []
    for player in soup.find_all("tr", attrs={"class": "player-row"}):
        role = player.find("span", attrs={"class": "role"})["data-value"]
        code = FantacalcioPuntoItWebsite.strip_player_id_from_url(
            player.find("a", attrs={"class": "player-name player-link"})["href"]
        )
        name = player.find("th", attrs={"class": "player-name"}).text
        team = player.find("td", attrs={"class": "player-team"}).text
        price_initial = player.find(
            "td", attrs={"class": "player-classic-initial-price"}
        ).text
        price_current = player.find(
            "td", attrs={"class": "player-classic-current-price"}
        ).text
        output.append(
            FpiPlayer(
                season_id=season_id,
                load_ts=load_ts,
                team_id=strip_whitespaces_and_newlines(team),
                name=strip_whitespaces_and_newlines(name),
                code_fpi=code,
                role=translate_role(role),
                price_initial=price_initial,
                price_current=price_current,
            ).to_namedtuple()
        )
    if not output:
        raise ValueError("No player match was found in the page.")
    return output


def _log_info_hit_max_seasons_to_scrape(max_match_days_to_scrape) -> None:
    LOGGER.info(
        "Reached the maximum number of match days to scrape (%s).",
        max_match_days_to_scrape,
    )


def _log_info_season_being_extracted(season_id: str) -> None:
    LOGGER.info("Extracting matches for season %s...", season_id)
