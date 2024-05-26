"""Extract data to populate the st_match table."""

import logging
import random
import time
from datetime import datetime
from typing import NamedTuple, Self

from pydantic import Field, NonNegativeInt

from serie_a_db.data_extraction.clients.lega_serie_a_website import SerieAWebsite
from serie_a_db.data_extraction.input_base_model import DbInputBaseModel
from serie_a_db.data_extraction.table_specific_extractors.dm_match_day import Status
from serie_a_db.db.client import Db

LOGGER = logging.getLogger(__name__)


class Match(DbInputBaseModel):
    """Representation of a match in the Serie A championship."""

    match_day_id: str
    match_code_serie_a_api: int
    home_team_id: str
    home_team_name: str
    home_goals: NonNegativeInt
    home_penalty_goals: NonNegativeInt
    home_schema: str
    home_coach_code_serie_a_api: int
    home_coach_name: str
    home_coach_surname: str
    away_team_id: str
    away_team_name: str
    away_goals: NonNegativeInt
    away_penalty_goals: NonNegativeInt
    away_schema: str
    away_coach_code_serie_a_api: int
    away_coach_name: str
    away_coach_surname: str
    status: Status
    date: str
    time: str
    time_zone: str
    duration_minutes: int | None = Field(ge=0, le=120)

    @classmethod
    def fake(cls, **kwargs) -> Self:
        """Generate a match object with overwritable default values for all fields."""
        data = {
            "match_day_id": "S24M01",
            "match_code_serie_a_api": 123,
            "away_team_id": "FOO",
            "away_team_name": "Foo",
            "home_team_id": "BAR",
            "home_team_name": "Bar",
            "away_goals": 1,
            "away_penalty_goals": 0,
            "home_goals": 2,
            "home_penalty_goals": 1,
            "away_schema": "4-4-2",
            "home_schema": "4-3-3",
            "duration_minutes": None,
            "date": "2024-10-01",
            "time": "20:45:00",
            "time_zone": "UTC+2",
            "status": Status.COMPLETED,
            "away_coach_code_serie_a_api": 123,
            "away_coach_name": "Baz",
            "away_coach_surname": "Qux",
            "home_coach_code_serie_a_api": 456,
            "home_coach_name": "Zap",
            "home_coach_surname": "Fiz",
        } | kwargs
        return cls(**data)  # type: ignore


def scrape_match_data(
    db: Db | None = None,
    serie_a_website_client: SerieAWebsite | None = None,
    sleep_time: int = 10,
    max_match_days_to_scrape: int = 38,
) -> list[NamedTuple]:
    """Extract match data."""
    if db is None:
        db = Db()
    if serie_a_website_client is None:
        serie_a_website_client = SerieAWebsite()

    match_days_to_import = _get_match_days_to_import(db)

    matches = []
    for index, (match_day_id, match_day_api_code) in enumerate(
        match_days_to_import, start=1
    ):
        if index > max_match_days_to_scrape:
            LOGGER.info(
                "Reached the maximum number of match days to scrape (%s).",
                max_match_days_to_scrape,
            )
            break

        LOGGER.info(
            "Extracting matches for match day %s (%s)...",
            match_day_id,
            match_day_api_code,
        )
        match_day_page = serie_a_website_client.get_match_day_page(match_day_api_code)

        for match in match_day_page["data"]:
            obj = api_response_to_match(match_day_id, match).to_namedtuple()
            matches.append(obj)

        # Sleep to avoid overloading the website
        seconds_sleep = random.randint(sleep_time - 5, sleep_time + 5)
        time.sleep(seconds_sleep)

    return matches


def api_response_to_match(match_day_id: str, match: dict) -> Match:
    """Convert API response to a match object."""
    return Match(
        match_day_id=match_day_id,
        match_code_serie_a_api=match["match_id"],
        away_team_id=match["away_team_short_name"],
        away_team_name=match["away_team_name"].title(),
        home_team_id=match["home_team_short_name"],
        home_team_name=match["home_team_name"].title(),
        away_goals=match["away_goal"],
        away_penalty_goals=match["away_penalty_goal"],
        home_goals=match["home_goal"],
        home_penalty_goals=match["home_penalty_goal"],
        away_schema=match["away_schema"].replace(" ", ""),
        home_schema=match["home_schema"].replace(" ", ""),
        duration_minutes=_extract_minutes(match["minutes_played"]),
        date=_extract_date(match["date_time"]),
        time=match["match_hm"],
        time_zone="UTC+2",
        status=_map_status(match["match_status"]),
        away_coach_code_serie_a_api=match["away_coach_id"],
        away_coach_name=match["away_coach_name"].title(),
        away_coach_surname=match["away_coach_surname"].title(),
        home_coach_code_serie_a_api=match["home_coach_id"],
        home_coach_name=match["home_coach_name"].title(),
        home_coach_surname=match["home_coach_surname"].title(),
    )


def _extract_minutes(minutes_str: str) -> int | None:
    if minutes_str == "":
        return None
    minutes = int(minutes_str.split("'")[0]) + 1
    if minutes > 120:
        return None
    return minutes


def _get_match_days_to_import(db: Db) -> list[tuple[str, int]]:
    """Get match days to import.

    Args:
    ----
        db: Database client.

    Returns:
    -------
        List of tuples in the form (match_day_id, match_day_code_serie_a_api).

    """
    try:
        # The two tables should always be available
        query = """
        SELECT
            dmmd.match_day_id,
            dmmd.code_serie_a_api
        FROM dm_match_day AS dmmd
            LEFT JOIN st_match AS st
                ON dmmd.match_day_id = st.match_day_id
        WHERE
            dmmd.status = 'ongoing'
            OR st.match_day_id IS NULL
        ORDER BY
            dmmd.match_day_id;
        """
        return db.select(query)
    finally:
        db.close_connection()


def _extract_date(datetime_str: str) -> str:
    """Extract date from datetime string."""
    return datetime.fromisoformat(datetime_str).date().isoformat()


def _map_status(external_status: int) -> Status:
    """Map status."""
    _map = {
        0: Status.UPCOMING,
        1: Status.ONGOING,
        2: Status.COMPLETED,
    }
    try:
        return _map[external_status]
    except KeyError as err:
        msg = f"Cannot handle unknown match status {external_status}"
        raise ValueError(msg) from err
