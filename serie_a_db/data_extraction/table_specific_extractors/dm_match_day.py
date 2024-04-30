"""Extract data to populate the dm_match_day table."""

from pydantic import Field

from serie_a_db.data_extraction.input_base_model import DbInputBaseModel


class MatchDay(DbInputBaseModel):
    """Match day data model."""

    season_id: str
    code_serie_a_api: int
    number: int = Field(ge=1, le=38)
    active: int = Field(ge=0, le=1)
