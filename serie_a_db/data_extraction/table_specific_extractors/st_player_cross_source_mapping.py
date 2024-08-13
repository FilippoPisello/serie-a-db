"""Perform the players matching across different sources."""

import logging
from typing import NamedTuple, Self

from pydantic import BaseModel, PositiveInt
from thefuzz import fuzz  # type: ignore

from serie_a_db.data_extraction.input_base_model import DbInputBaseModel
from serie_a_db.data_extraction.table_specific_extractors.shared_definitions import (
    PlayerRole,
    get_relevant_season,
)
from serie_a_db.db.client import Db

LOGGER = logging.getLogger(__name__)

MIN_ACCEPTED_SIMILIARITY = 80


class PlayerMapping(DbInputBaseModel):
    """Mapping between two sources for a player.

    Allows to identify the same player across different sources.
    """

    season_id: str
    code_fpi: int
    code_fm: int


class PlayerRecord(BaseModel):
    """Generic player record."""

    code: PositiveInt
    name: str
    role: PlayerRole

    def __hash__(self) -> int:
        """Use the code as hash."""
        return self.code

    def __eq__(self, other: object) -> bool:
        """Two players are equal if they have the same name and role."""
        if not isinstance(other, PlayerRecord):
            return NotImplemented
        return (self.name == other.name) and (self.role == other.role)

    @classmethod
    def fake(cls, **kwargs) -> Self:
        """Create a fake player record for testing."""
        data = {
            "code": 1,
            "name": "Foo",
            "role": PlayerRole.ATTACKER,
        } | kwargs
        return cls(**data)  # type: ignore


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
    output: dict[str, set[PlayerRecord]] = {}
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


def find_player_mappings(  # noqa: PLR0912
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
        for player_fm in set(team_players_fm):

            best_match = (PlayerRecord.fake(), 0)

            for player_fpi in set(players_fpi_copy[team_id]):
                score = fuzz.partial_ratio(player_fm.name, player_fpi.name)
                # Update the best match if new pair is better
                if score > best_match[1]:
                    best_match = (player_fpi, score)

            if best_match[1] >= MIN_ACCEPTED_SIMILIARITY:
                mappings.append(
                    PlayerMapping(
                        season_id=season_id,
                        code_fpi=best_match[0].code,
                        code_fm=player_fm.code,
                    ).to_namedtuple()
                )
                players_fpi_copy[team_id].remove(best_match[0])
                players_fm_copy[team_id].remove(player_fm)

    unmatched_players = _regroup_unmatched_players(players_fm_copy)
    if unmatched_players:
        LOGGER.warning("%s players could not be matched", len(unmatched_players))
    return mappings


def _regroup_unmatched_players(
    players_fm: dict[str, set[PlayerRecord]]
) -> set[PlayerRecord]:
    unmatched_players: set[PlayerRecord] = set()
    for _, team_players_fm in players_fm.items():
        unmatched_players = unmatched_players.union(team_players_fm)
    return unmatched_players
