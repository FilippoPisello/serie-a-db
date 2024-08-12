"""Import the player list from Fantamaster."""

from typing import NamedTuple

from pydantic import PositiveInt

from serie_a_db.data_extraction.clients.fantamaster import FantamasterWebsite
from serie_a_db.data_extraction.input_base_model import DbInputBaseModel
from serie_a_db.data_extraction.table_specific_extractors.shared_definitions import (
    PlayerRole,
)
from serie_a_db.data_extraction.table_specific_extractors.st_fpi_player_match import (
    translate_role,
)
from serie_a_db.db.client import Db
from serie_a_db.utils import now


class FmPlayer(DbInputBaseModel):
    """A player from the player list of Fantamaster."""

    load_ts: str
    season_id: str
    team_id: str
    code_fm: int
    name: str
    role: PlayerRole
    value: PositiveInt


def scrape_player_data(
    db: Db | None = None,
    website_client: FantamasterWebsite | None = None,
) -> list[NamedTuple]:
    """Scape player data from the Fantamaster website."""
    if db is None:
        db = Db()
    if website_client is None:
        website_client = FantamasterWebsite()

    season_id = _get_season_data_is_about(db)
    load_ts = now().isoformat(sep=" ", timespec="milliseconds")

    raw_players = FantamasterWebsite.get_players()
    parsed_players = [
        FmPlayer(
            load_ts=load_ts,
            season_id=season_id,
            team_id=player["team"].upper()[:3],
            code_fm=player["id"],
            name=player["name"],
            role=translate_role(player["role"]),
            value=player["value"],
        ).to_namedtuple()
        for player in raw_players
    ]
    return parsed_players


def _get_season_data_is_about(db: Db) -> str:
    try:
        query = """
        SELECT MIN(season_id)
        FROM dm_season
        WHERE
            status IN ('ongoing', 'upcoming')
        """
        return db.select(query)[0][0]
    finally:
        db.close_connection()
