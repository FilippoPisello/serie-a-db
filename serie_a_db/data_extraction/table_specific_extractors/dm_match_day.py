"""Extract data to populate the dm_match_day table."""

from pydantic import Field

from serie_a_db.data_extraction.clients.lega_serie_a_website import SerieAWebsite
from serie_a_db.data_extraction.input_base_model import DbInputBaseModel
from serie_a_db.data_extraction.table_specific_extractors.shared_values import Status
from serie_a_db.db.client import Db
from serie_a_db.exceptions import NoSuchTableError


class MatchDay(DbInputBaseModel):
    """Match day data model."""

    season_code_serie_a_api: int
    code_serie_a_api: int
    number: int = Field(ge=1, le=38)
    status: Status


def scrape_match_day_data(
    db: Db | None = None,
    serie_a_website_client: SerieAWebsite | None = None,
) -> list[MatchDay]:
    """Extract match day data."""
    # Facilitate replacement with mocks for testing
    if db is None:
        db = Db()
    if serie_a_website_client is None:
        serie_a_website_client = SerieAWebsite()

    season_codes = _get_season_codes(db)
    return _scrape_match_day_data_from_the_web(serie_a_website_client, season_codes)


def _get_season_codes(db: Db) -> set[int]:
    """Get the season codes from the database."""
    try:
        season_codes = db.select("SELECT code_serie_a_api FROM dm_season")
    except NoSuchTableError:
        return set()
    return {row[0] for row in season_codes}


def _scrape_match_day_data_from_the_web(
    serie_a_website_client: SerieAWebsite, season_codes: set[int]
) -> list[MatchDay]:
    """Scrape match day data from the web."""
    data = []
    for season_code in season_codes:
        season_page = serie_a_website_client.get_season_page(season_code)
        for match_day in season_page["data"]:
            data.append(
                MatchDay(
                    season_code_serie_a_api=season_code,
                    code_serie_a_api=match_day["id_category"],
                    number=int(match_day["description"]),
                    status=_map_status(match_day["category_status"]),
                ).to_namedtuple()
            )
    return data


def _map_status(external_status: str) -> Status:
    _map = {"PLAYED": Status.COMPLETED, "TO BE PLAYED": Status.UPCOMING}
    try:
        return _map[external_status]
    except KeyError as err:
        msg = f"Cannot handle unknown match status {external_status}"
        raise ValueError(msg) from err
