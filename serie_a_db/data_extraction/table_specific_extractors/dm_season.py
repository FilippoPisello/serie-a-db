"""Logic to update the dm_season table."""

from typing import NamedTuple

from bs4 import BeautifulSoup, NavigableString

from serie_a_db.data_extraction.clients.lega_serie_a_website import SerieAWebsite
from serie_a_db.data_extraction.input_base_model import DbInputBaseModel
from serie_a_db.db.client import Db


class Season(DbInputBaseModel):
    """Season data model."""

    year_start: int
    code_serie_a_api: int
    active: int


def scrape_dm_season_data(
    db: Db | None = None,
    serie_a_website_client: SerieAWebsite | None = None,
) -> list[NamedTuple]:
    """Extract season data."""
    # Facilitate replacement with mocks for testing
    if db is None:
        db = Db()
    if serie_a_website_client is None:
        serie_a_website_client = SerieAWebsite()

    min_season = establish_earliest_season_to_look_for(db)
    return scrape_data_from_the_web(serie_a_website_client, min_season)


def establish_earliest_season_to_look_for(db: Db) -> int:
    """Look for data from the active season onwards.

    The active season might become inactive and a new season might start,
    everything in the past is instead fixed and does not need to be updated.
    """
    # Get active season from the database
    res = db.select("SELECT year_start FROM dm_season WHERE active = 1")
    if res:
        return res[0][0]
    # Never go earlier than 2000
    return 2000


def scrape_data_from_the_web(
    serie_a_website_client: SerieAWebsite,
    min_season: int,
) -> list[NamedTuple]:
    """Extract season data from the web."""
    homepage = serie_a_website_client.get_homepage()
    seasons = []
    for season_year_start, season_api_code in _find_seasons(homepage):

        if season_year_start < min_season:
            continue

        season_page = serie_a_website_client.get_season_page(season_api_code)
        season = Season(
            year_start=season_year_start,
            code_serie_a_api=season_api_code,
            active=_find_is_active_season(season_page),
        )
        seasons.append(season.to_namedtuple())

    return seasons


def _find_seasons(homepage: str) -> list[tuple[int, int]]:
    """Extract the seasons from the homepage."""
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


def _find_is_active_season(season_response: dict) -> bool:
    """Extract if the season is active."""
    data = season_response["data"]
    # The season is active if any game day is still to be played
    return any(game_day["category_status"] == "TO BE PLAYED" for game_day in data)