"""Perform the players matching across different sources."""

from difflib import SequenceMatcher
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
    role: PlayerRole

    def __hash__(self) -> int:
        return self.code

    def __eq__(self, other: Self) -> bool:
        return (self.name == other.name) and (self.role == other.role)

    @classmethod
    def fake(cls, **kwargs) -> Self:
        data = {
            "code": 1,
            "name": "Foo",
            "role": PlayerRole.ATTACKER,
        } | kwargs
        return cls(**data)


def derive_mappings(db: Db | None = None) -> list[NamedTuple]:
    """Use the db data to derive the cross-source matches."""
    if db is None:
        db = Db()

    season_id = get_relevant_season(db, close_connection=False)

    players_fpi, players_fm = _get_players_from_db(db)

    mappings = find_player_mappings(players_fpi, players_fm, season_id)

    return mappings


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
        fpi = db.select(query.replace("$SOURCE$", "fpi"))
        fm = db.select(query.replace("$SOURCE$", "fm"))
        return _structure(fpi), _structure(fm)
    finally:
        db.close_connection()


def _structure(raw_records: list[tuple]) -> dict[str, set[PlayerRecord]]:
    output = {}
    for record in raw_records:
        # Create a new team set if not already there
        if record[2] not in output:
            output[record[2]] = set()

        # Add record
        output[record[2]].add(
            PlayerRecord(
                code=record[0],
                name=record[1].lower(),
                role=record[3],
            )
        )
    return output


def find_player_mappings(
    players_fpi: dict[str, set[PlayerRecord]],
    players_fm: dict[str, set[PlayerRecord]],
    season_id: str,
) -> list[NamedTuple]:
    """Find the player mappings using different strategies."""
    mappings = []
    players_fpi_copy = players_fpi.copy()
    players_fm_copy = players_fm.copy()

    # First consider mappings by name, team, role
    for team_id, team_players_fm in players_fm_copy.items():
        # Need to wrap over set to create a copy and be able to modify the
        # existing main structures
        for player_fm in set(team_players_fm):
            for player_fpi in set(players_fpi_copy[team_id]):
                if player_fm == player_fpi:
                    mappings.append(
                        PlayerMapping(
                            season_id=season_id,
                            code_fpi=player_fpi.code,
                            code_fm=player_fm.code,
                        ).to_namedtuple()
                    )
                    players_fpi_copy[team_id].remove(player_fpi)
                    players_fm_copy[team_id].remove(player_fm)

    # Then consider mappings by name, team
    for team_id, team_players_fm in players_fm_copy.items():
        # Need to wrap over set to create a copy and be able to modify the
        # existing main structures
        for player_fm in set(team_players_fm):
            for player_fpi in set(players_fpi_copy[team_id]):
                if player_fm.name == player_fpi.name:
                    mappings.append(
                        PlayerMapping(
                            season_id=season_id,
                            code_fpi=player_fpi.code,
                            code_fm=player_fm.code,
                        ).to_namedtuple()
                    )
                    players_fpi_copy[team_id].remove(player_fpi)
                    players_fm_copy[team_id].remove(player_fm)

    # Then consider mappings by name fuzzy matching, team
    for team_id, team_players_fm in players_fm_copy.items():
        # Need to wrap over set to create a copy and be able to modify the
        # existing main structures
        best_match = (None, 0)
        for player_fm in set(team_players_fm):
            for player_fpi in set(players_fpi_copy[team_id]):
                score = SequenceMatcher(None, player_fm.name, player_fpi.name).ratio()
                # Update the best match if new pair is better
                if score > best_match[1]:
                    best_match = (player_fpi, score)

            if best_match[1] >= 0.8:
                mappings.append(
                    PlayerMapping(
                        season_id=season_id,
                        code_fpi=best_match[0].code,
                        code_fm=player_fm.code,
                    ).to_namedtuple()
                )
                players_fpi_copy[team_id].remove(player_fpi)
                players_fm_copy[team_id].remove(player_fm)

    _raise_error_if_fm_players_without_a_match(players_fm_copy)

    return mappings


def _raise_error_if_fm_players_without_a_match(
    players_fm_copy: dict[str, set[PlayerRecord]]
) -> None:
    unmatched_players = set()
    for _, team_players_fm in players_fm_copy.items():
        unmatched_players = unmatched_players.union(team_players_fm)
    if unmatched_players:
        players_str = "\n".join(str(player) for player in unmatched_players)
        raise ValueError(f"Could not match these players:\n{players_str}")
