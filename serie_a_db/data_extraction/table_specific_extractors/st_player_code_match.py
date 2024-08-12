"""Perform the players matching across different sources."""

from typing import NamedTuple, Self

from pydantic import BaseModel, Field, PositiveInt

from serie_a_db.data_extraction.input_base_model import DbInputBaseModel
from serie_a_db.data_extraction.table_specific_extractors.shared_definitions import (
    PlayerRole,
    get_relevant_season,
)
from serie_a_db.db.client import Db


class PlayerMapping(DbInputBaseModel):
    season_id: str
    code_fpi: int
    code_fm: int


class PlayerRecord(BaseModel):
    code: PositiveInt
    name: str
    team_id: str = Field(min_length=3, max_length=3)
    role: PlayerRole

    def __hash__(self) -> int:
        return self.code

    def is_equal(
        self, other: Self, attributes: tuple[str] = ("name", "team_id", "role")
    ) -> bool:
        for attr in attributes:
            if getattr(self, attr) != getattr(other, attr):
                return False
        return True

    @classmethod
    def fake(cls, **kwargs) -> Self:
        data = {
            "code": 1,
            "name": "Foo",
            "team_id": "JUV",
            "role": PlayerRole.ATTACKER,
        } | kwargs
        return cls(**data)


def derive_mappings(db: Db | None = None) -> list[NamedTuple]:
    """Use the db data to derive the cross-source matches."""
    if db is None:
        db = Db()

    season_id = get_relevant_season(db)

    players_fpi, players_fm = _get_players_from_db(db)

    mappings = find_player_mappings(players_fpi, players_fm, season_id)


def _get_players_from_db(
    db: Db,
) -> tuple[dict[str, set[PlayerRecord]], dict[str, set[PlayerRecord]]]:
    """Return two data structures in the form {team_id : {player_set}}."""
    try:
        query = """
        SELECT
            code_$SOURCE$ AS code,
            name,
            team_id,
            role
        FROM st_$SOURCE$_player
        WHERE load_ts = (SELECT MAX(load_ts) FROM st_$SOURCE$_player)
        """
        fpi = db.select(query.replace("%SOURCE$", "fpi"))
        fm = db.select(query.replace("%SOURCE$", "fm"))
        return _structure(fpi), _structure(fm)
    finally:
        db.close_connection()


def _structure(raw_records: list[tuple]) -> dict[set[PlayerRecord]]:
    output = {}
    for record in raw_records:
        if record[2] not in output:
            output[record[2]] = set()
        output[record[2]].add()
    return {
        PlayerRecord(
            code=record[0],
            name=record[1].lower(),
            team_id=record[2],
            role=record[3],
        )
        for record in raw_records
    }


def find_player_mappings(
    players_fpi: set[PlayerRecord], players_fm: set[PlayerRecord], season_id: str
) -> list[NamedTuple]:
    mappings = []
    players_fpi_copy = players_fpi.copy()
    players_fm_copy = players_fm.copy()

    # First considers mappings by name, team, role
    for player_fm in set(players_fm_copy):
        for player_fpi in set(players_fpi_copy):
            if player_fm.is_equal(player_fpi):
                mappings.append(
                    PlayerMapping(
                        season_id=season_id,
                        code_fpi=player_fpi.code,
                        code_fm=player_fm.code,
                    ).to_namedtuple()
                )
                players_fm_copy.remove(player_fm)
                players_fpi_copy.remove(player_fpi)

    # Then by name, team only
    for player_fm in set(players_fm_copy):
        for player_fpi in set(players_fpi_copy):
            if player_fm.is_equal(player_fpi, attributes=("name", "team_id")):
                mappings.append(
                    PlayerMapping(
                        season_id=season_id,
                        code_fpi=player_fpi.code,
                        code_fm=player_fm.code,
                    ).to_namedtuple()
                )
                players_fm_copy.remove(player_fm)
                players_fpi_copy.remove(player_fpi)

    # Then by name only
    for player_fm in set(players_fm_copy):
        for player_fpi in set(players_fpi_copy):
            if player_fm.is_equal(player_fpi, attributes=("name")):
                mappings.append(
                    PlayerMapping(
                        season_id=season_id,
                        code_fpi=player_fpi.code,
                        code_fm=player_fm.code,
                    ).to_namedtuple()
                )
                players_fm_copy.remove(player_fm)
                players_fpi_copy.remove(player_fpi)

    return mappings
