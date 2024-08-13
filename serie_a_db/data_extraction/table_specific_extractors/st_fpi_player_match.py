"""Logic to extract data from the website fantacalcio.it."""

import logging
from typing import NamedTuple

from bs4 import BeautifulSoup, Tag
from pydantic import NonNegativeInt

from serie_a_db.data_extraction.clients.fantacalcio_punto_it_website import (
    FantacalcioPuntoItWebsite,
)
from serie_a_db.data_extraction.input_base_model import DbInputBaseModel
from serie_a_db.data_extraction.table_specific_extractors.shared_definitions import (
    PlayerRole,
    log_fatal_error,
    sleep_not_to_overload_the_website,
)
from serie_a_db.db.client import Db
from serie_a_db.utils import strip_whitespaces_and_newlines

LOGGER = logging.getLogger(__name__)


class PlayerMatch(DbInputBaseModel):
    """Info about the performance of a player in a match."""

    match_day_id: str
    team_name: str
    name: str
    code_fpi: int
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
    yellow_card: bool
    red_card: bool
    subbed_in: bool
    subbed_out: bool


def scrape_player_match_data(
    db: Db | None = None,
    website_client: FantacalcioPuntoItWebsite | None = None,
    sleep_time: int = 15,
    max_match_days_to_scrape: int = 1,
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
        except ValueError:
            log_fatal_error(LOGGER, match_day_id, "match day")
            break

        sleep_not_to_overload_the_website(sleep_time)

    return player_matches


def _get_match_days_to_import(db: Db) -> list[tuple[int, int, str]]:
    try:
        query = """
        SELECT
            dms.year_start,
            dmmd.number,
            dmmd.match_day_id
        FROM dm_match_day AS dmmd
            INNER JOIN dm_season AS dms ON dmmd.season_id = dms.season_id
            LEFT JOIN st_fpi_player_match AS st ON dmmd.match_day_id = st.match_day_id
        WHERE
            dmmd.status = 'completed'
            -- Data on the website starts from season 2015/16
            AND dms.year_start >= 2015
        GROUP BY dmmd.match_day_id
        HAVING IFNULL(COUNT(DISTINCT st.team_name), 0) < 20
            OR IFNULL(COUNT(DISTINCT st.code_fpi), 0) < (20 * 12)
        ORDER BY dms.year_start DESC,
            dmmd.number
        """
        return db.select(query)
    finally:
        db.close_connection()


def parse_match_day_page(grades_page: str, match_day_id: str) -> list[NamedTuple]:
    """Parse the page of a match day to extract a list of player matches."""
    soup = BeautifulSoup(grades_page, "html.parser")
    team_tables = soup.find_all("li", attrs={"class": "team-table"})

    output = []

    for team in team_tables:
        head = team.find("thead")
        team_name = head.find("a", attrs={"class": "team-name team-link"}).text

        body = team.find("tbody")
        for player in body.find_all("tr"):
            ids, grades, bonuses = player.find_all("td")

            role = ids.find("span", attrs={"class": "role"})["data-value"]
            # No need to extract the coach
            if role == "all":
                continue

            name = ids.text
            url = ids.find("a", attrs={"class": "player-name player-link"})["href"]
            code = FantacalcioPuntoItWebsite.strip_player_id_from_url(url)
            subbed_in = "Icona subentrato" in str(ids)
            subbed_out = "Icona sostituito" in str(ids)

            website, ita, stats = grades.find_all("div", attrs={"class": "pill"})
            website_grade, website_fanta_grade = _parse_grades(website)
            ita_grade, ita_fanta_grade = _parse_grades(ita)
            stats_grade, stats_fanta_grade = _parse_grades(stats)
            yellow_card = "yellow-card" in str(grades)
            red_card = "red-card" in str(grades)

            goals_scored = _extract_bonus(bonuses, "Gol segnati")
            goals_conceded = _extract_bonus(bonuses, "Gol subiti")
            own_goals = _extract_bonus(bonuses, "Autoreti")
            penalties_scored = _extract_bonus(bonuses, "Rigori segnati")
            penalties_missed = _extract_bonus(bonuses, "Rigori sbagliati")
            penalties_saved = _extract_bonus(bonuses, "Rigori parati")
            assists = _extract_bonus(bonuses, "Assist")

            output.append(
                PlayerMatch(
                    match_day_id=match_day_id,
                    team_name=strip_whitespaces_and_newlines(team_name),
                    name=strip_whitespaces_and_newlines(name),
                    code_fpi=code,
                    role=translate_role(role),
                    fantacalcio_punto_it_grade=website_grade,
                    fantacalcio_punto_it_fanta_grade=website_fanta_grade,
                    italia_grade=ita_grade,
                    italia_fanta_grade=ita_fanta_grade,
                    statistical_grade=stats_grade,
                    statistical_fanta_grade=stats_fanta_grade,
                    goals_scored=goals_scored,
                    goals_conceded=goals_conceded,
                    own_goals=own_goals,
                    penalties_scored=penalties_scored,
                    penalties_missed=penalties_missed,
                    penalties_saved=penalties_saved,
                    assists=assists,
                    yellow_card=yellow_card,
                    red_card=red_card,
                    subbed_in=subbed_in,
                    subbed_out=subbed_out,
                ).to_namedtuple()
            )
    if not output:
        raise ValueError("No player match was found in the page.")
    return output


def _parse_grades(pill: Tag) -> tuple[float, float]:
    grade = pill.find("span", attrs={"class": "player-grade"})["data-value"]  # type: ignore
    fanta_grade = pill.find("span", attrs={"class": "player-fanta-grade"})["data-value"]  # type: ignore
    return float(grade.replace(",", ".")), float(fanta_grade.replace(",", "."))  # type: ignore


def _extract_bonus(bonus: Tag, bonus_name: str) -> int:
    bonus_value = bonus.find("span", attrs={"title": bonus_name})
    return int(bonus_value["data-value"])  # type: ignore


def translate_role(role: str) -> PlayerRole:
    """Convert a role string in italian to a PlayerRole."""
    _map = {
        "p": PlayerRole.GOALKEEPER,
        "d": PlayerRole.DEFENDER,
        "c": PlayerRole.MIDFIELDER,
        "a": PlayerRole.ATTACKER,
    }
    return _map[role.lower()]


def _log_info_hit_max_matches_to_scrape(max_match_days_to_scrape) -> None:
    LOGGER.info(
        "Reached the maximum number of match days to scrape (%s).",
        max_match_days_to_scrape,
    )


def _log_info_match_day_being_extracted(match_day_id: str) -> None:
    LOGGER.info("Extracting matches for match day %s...", match_day_id)
