import logging
import random
from enum import StrEnum
from time import time
from typing import NamedTuple

from pydantic import BaseModel, Field, NonNegativeInt, ValidationError

from serie_a_db.data_extraction.clients.fantacalcio_punto_it_website import (
    FantacalcioPuntoItWebsite,
)
from serie_a_db.data_extraction.input_base_model import DbInputBaseModel
from serie_a_db.db.client import Db

LOGGER = logging.getLogger(__name__)


class PlayerRole(StrEnum):
    GOALKEEPER = "P"
    DEFENDER = "D"
    MIDFIELDER = "C"
    STRIKER = "A"
    COACH = "ALL"


class PlayerMatch(DbInputBaseModel):
    match_day_id: str
    team_name: str
    name: str
    code: int
    role: PlayerRole
    fantacalcio_punto_it_grade: float
    fantacalcio_punto_it_fanta_grade: float
    italia_grade: float
    italia_fanta_grade: float
    statistical_grade: float
    statistical_fanta_grade: float
    goals_scored: NonNegativeInt
    goals_conceded: NonNegativeInt
    own_goals: NonNegativeInt
    penalties_scored: NonNegativeInt
    penalties_missed: NonNegativeInt
    penalties_saved: NonNegativeInt
    assists: NonNegativeInt
    man_of_the_match: bool


def scrape_player_match_data(
    db: Db | None = None,
    website_client: FantacalcioPuntoItWebsite | None = None,
    sleep_time: int = 15,
    max_match_days_to_scrape: int = 38 * 10,
) -> list[NamedTuple]:
    """Extract data about players performance in a match."""
    if db is None:
        db = Db()
    if website_client is None:
        website_client = FantacalcioPuntoItWebsite()

    match_days_to_import = _get_match_days_to_import(db)

    player_matches = []
    for index, (season_year_start, match_day_number, match_day_id) in enumerate(
        match_days_to_import, start=1
    ):
        if index > max_match_days_to_scrape:
            _log_info_hit_max_matches_to_scrape(max_match_days_to_scrape)
            break

        _log_info_match_day_being_extracted(match_day_id)
        match_day_results_page = website_client.get_grades_page(
            season_year_start, match_day_number
        )

        # Try getting all the matches for the match day. If one fails, stop
        # without erroring out so that what successfully extracted so far
        # is still imported
        try:
            player_matches.extend(
                parse_match_day_page(match_day_results_page, match_day_id)
            )
        except ValidationError as err:
            _log_warn_validation_error(match_day_id, err)
            break

        _sleep_not_to_overload_the_website(sleep_time)

    return player_matches


def _get_match_days_to_import(db: Db) -> list[tuple[int, int, str]]: ...


def parse_match_day_page(grades_page: str, match_day_id: str) -> list[NamedTuple]: ...


def _sleep_not_to_overload_the_website(sleep_time: int) -> None:
    seconds_sleep = random.randint(sleep_time - 5, sleep_time + 5)
    time.sleep(seconds_sleep)


def _log_info_hit_max_matches_to_scrape(max_match_days_to_scrape) -> None:
    LOGGER.info(
        "Reached the maximum number of match days to scrape (%s).",
        max_match_days_to_scrape,
    )


def _log_info_match_day_being_extracted(match_day_id: str) -> None:
    LOGGER.info("Extracting matches for match day %s...", match_day_id)


def _log_warn_validation_error(match_day_id, err) -> None:
    LOGGER.warning(
        "Stopping the extraction at match day %s due to error: %s",
        match_day_id,
        err,
    )
