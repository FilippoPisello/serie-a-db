"""Extract data to populate the st_match table."""

from typing import Self

from pydantic import Field, NonNegativeInt

from serie_a_db.data_extraction.input_base_model import DbInputBaseModel
from serie_a_db.data_extraction.table_specific_extractors.dm_match_day import Status


class Match(DbInputBaseModel):
    """Representation of a match in the Serie A championship."""

    match_code_serie_a_api: int
    away_team_id: str
    away_team_name: str
    home_team_id: str
    home_team_name: str
    away_goals: NonNegativeInt
    away_penalty_goals: NonNegativeInt
    home_goals: NonNegativeInt
    home_penalty_goals: NonNegativeInt
    away_schema: str
    home_schema: str
    duration_minutes: int = Field(ge=0, le=120)
    date: str
    time: str
    status: Status
    away_coach_code_serie_a_api: int
    away_coach_name: str
    away_coach_surname: str
    home_coach_code_serie_a_api: int
    home_coach_name: str
    home_coach_surname: str

    @classmethod
    def fake(cls, **kwargs) -> Self:
        data = {
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
            "duration_minutes": 90,
            "date": "2024-01-01",
            "time": "20:45",
            "status": Status.COMPLETED,
            "away_coach_code_serie_a_api": 123,
            "away_coach_name": "Baz",
            "away_coach_surname": "Qux",
            "home_coach_code_serie_a_api": 456,
            "home_coach_name": "Zap",
            "home_coach_surname": "Fiz",
        } | kwargs
        return cls(**data)
