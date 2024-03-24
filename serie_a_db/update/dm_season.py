"""Logic to update the dm_season table."""

from typing import NamedTuple

from bs4 import BeautifulSoup, NavigableString

from serie_a_db.input_base_model import DbInputBaseModel
from serie_a_db.scrape.lega_serie_a_website import SerieAWebsite
from serie_a_db.update.update import DbTable


class Season(DbInputBaseModel):
    """Season data model."""

    year_start: int
    code_serie_a_api: int
    active: int


class DmSeason(DbTable):
    """Update the season table."""

    SERIE_A_WEBSITE = SerieAWebsite()
    EARLIEST_SEASON = 2000

    def extract_data(self) -> list[NamedTuple]:
        """Extract season data from the web."""
        homepage = self.SERIE_A_WEBSITE.get_homepage()
        seasons = []
        for season_year_start, season_api_code in _find_seasons(homepage):

            if season_year_start < self.EARLIEST_SEASON:
                continue

            season_page = self.SERIE_A_WEBSITE.get_season_page(season_api_code)
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
