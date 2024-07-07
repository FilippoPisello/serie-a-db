"""Extract data to populate the dm_match_day table."""

import logging
from enum import StrEnum
from typing import NamedTuple, Self

from bs4 import BeautifulSoup, NavigableString
from pydantic import Field

from serie_a_db.data_extraction.clients.lega_serie_a_website import SerieAWebsite
from serie_a_db.data_extraction.input_base_model import DbInputBaseModel
from serie_a_db.db.client import Db
from serie_a_db.exceptions import NoSuchTableError

LOGGER = logging.getLogger(__name__)


class Status(StrEnum):
    """Match day status."""

    COMPLETED = "completed"
    ONGOING = "ongoing"
    UPCOMING = "upcoming"


class MatchDay(DbInputBaseModel):
    """Match day data model."""

    season_code_serie_a_api: int
    season_year_start: int
    code_serie_a_api: int
    number: int = Field(ge=1, le=38)
    status: Status

    @classmethod
    def fake(cls, **kwargs) -> Self:
        """Generate an instance with default values for all attributes.

        To be used for testing purposes. Specific attributes can be overridden
        by passing them as keyword arguments.
        """
        data = {
            "season_code_serie_a_api": 24,
            "season_year_start": 2024,
            "code_serie_a_api": 241,
            "number": 1,
            "status": Status.COMPLETED,
        } | kwargs
        return cls(**data)  # type: ignore

    @staticmethod
    def make_id(season_start_year: int, match_day_number: int) -> str:
        """Create a match day identifier."""
        year_str = str(season_start_year)
        return f"S{year_str[-2:]}M{match_day_number:02d}"


def scrape_match_day_data(
    db: Db | None = None,
    serie_a_website_client: SerieAWebsite | None = None,
) -> list[NamedTuple]:
    """Extract match day data."""
    # Facilitate replacement with mocks for testing
    if db is None:
        db = Db()
    if serie_a_website_client is None:
        serie_a_website_client = SerieAWebsite()

    all_seasons = _scape_seasons(serie_a_website_client)

    earliest_season = _get_earliest_season_to_import(db)
    relevant_seasons = _filter_seasons(all_seasons, earliest_season)

    return _scrape_match_day_data_from_the_web(serie_a_website_client, relevant_seasons)


def _get_earliest_season_to_import(db: Db) -> int:
    """Earliest between ongoing seasons and seasons with no match day data."""
    # Get active season from the database
    try:
        res = db.select(
            """
            SELECT
                MIN(dms.year_start)
            FROM dm_season AS dms
                LEFT JOIN dm_match_day_staging AS st
                    ON dms.year_start = st.season_year_start
            WHERE
                dms.status = 'ongoing' OR st.number IS NULL;
            """
        )
        return res[0][0]
    except (NoSuchTableError, IndexError):
        # Use minimum season if no active season is found
        return int(db.meta.get_parameter("include_seasons_from_year"))
    finally:
        db.close_connection()


def _scape_seasons(client: SerieAWebsite) -> list[tuple[int, int]]:
    """Scrape seasons from the Serie A website.

    Args:
    ----
        client: SerieAWebsite instance.

    Returns:
    -------
        List of tuples in the form (starting_year, serie_a_api_code).

    """
    homepage = client.get_homepage()
    soup = BeautifulSoup(homepage, "html.parser")
    selector = soup.find("select", attrs={"class": "hm-select", "name": "season"})

    if selector is None:
        raise ValueError("Season selector not found in the Serie A homepage.")
    if isinstance(selector, NavigableString):
        raise ValueError("Season selector has not the expected format.")

    return [
        (int(option.text[:4]), int(option["value"]))
        for option in selector.find_all("option")
    ]


def _filter_seasons(
    seasons: list[tuple[int, int]], earliest_season: int
) -> list[tuple[int, int]]:
    return [(year, code) for year, code in seasons if year >= earliest_season]


def _scrape_match_day_data_from_the_web(
    serie_a_website_client: SerieAWebsite, seasons: list[tuple[int, int]]
) -> list[NamedTuple]:
    """Scrape match day data from the web."""
    data = []
    for season_year_start, season_code in seasons:
        LOGGER.info("Scraping match days for season %d", season_year_start)
        season_page = serie_a_website_client.get_season_page(season_code)
        for match_day in season_page["data"]:
            data.append(
                MatchDay(
                    season_code_serie_a_api=season_code,
                    season_year_start=season_year_start,
                    code_serie_a_api=match_day["id_category"],
                    number=int(match_day["description"]),
                    status=_map_status(match_day["category_status"]),
                ).to_namedtuple()
            )
    return data


def _map_status(external_status: str) -> Status:
    _map = {
        "PLAYED": Status.COMPLETED,
        "TO BE PLAYED": Status.UPCOMING,
        "POSTPONED": Status.UPCOMING,
        "LIVE": Status.ONGOING,
    }
    try:
        return _map[external_status]
    except KeyError as err:
        msg = f"Cannot handle unknown match status {external_status}"
        raise ValueError(msg) from err
