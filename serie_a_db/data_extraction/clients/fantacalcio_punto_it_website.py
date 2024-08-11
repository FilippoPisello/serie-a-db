"""Get data from the website Fantacalcio.it."""

import re

import requests


class FantacalcioPuntoItWebsite:
    """Client to request data from the Fantacalcio.it website."""

    ROOT = "https://www.fantacalcio.it"

    @classmethod
    def get_grades_page(cls, season_year_start: int, match_day_number: int) -> str:
        """Get the raw HTML of the grades page."""
        season_tag = cls.make_season_tag(season_year_start)
        url = f"{cls.ROOT}/voti-fantacalcio-serie-a/{season_tag}/{match_day_number}"
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        return resp.text

    @classmethod
    def get_players_list_page(cls, season_year_start: int) -> str:
        """Get the raw HTML of the players list page."""
        season_tag = cls.make_season_tag(season_year_start)
        url = f"{cls.ROOT}/quotazioni-fantacalcio/{season_tag}"
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        return resp.text

    @staticmethod
    def make_season_tag(season_year_start: int) -> str:
        """Make the season tag in the format "2021-22"."""
        return f"{season_year_start}-{str(season_year_start + 1)[2:]}"

    @staticmethod
    def strip_player_id_from_url(player_url: str) -> int:
        """Get the player ID from the player URL."""
        # If url finishes like /YYYY-YY then the player ID is the penultimate part
        # otherwise it is the last part
        parts = player_url.split("/")
        if re.match(r"\d{4}-\d{2}", parts[-1]):
            return int(parts[-2])
        return int(parts[-1])
