"""Get data from the official Serie A website."""

from functools import lru_cache

import requests


class SerieAWebsite:
    """Client to request data from the Serie A website."""

    ROOT = "https://www.legaseriea.it"

    @classmethod
    def get_homepage(cls) -> str:
        """Get the raw HTML of the Serie A homepage."""
        resp = requests.get(f"{cls.ROOT}/en/serie-a", timeout=5)
        resp.raise_for_status()
        return resp.text

    @classmethod
    @lru_cache(maxsize=128)
    def get_season_page(cls, season_api_code: int) -> dict:
        """Get the API data for a single season."""
        resp = requests.get(
            f"{cls.ROOT}/api/season/{season_api_code}/championship/A/matchday?lang=eng",
            timeout=5,
        )
        resp.raise_for_status()
        return resp.json()

    @classmethod
    def get_match_day_page(cls, match_day_api_code: int) -> dict:
        """Get the API data for a single match day."""
        resp = requests.get(
            f"{cls.ROOT}/api/stats/live/match?extra_link&lang=en&match_day_id={match_day_api_code}",
            timeout=5,
        )
        resp.raise_for_status()
        return resp.json()

    @classmethod
    def get_matches(cls, match_day_api_code: int) -> list[dict]:
        """Get the matches only API data for a single match day."""
        return cls.get_match_day_page(match_day_api_code)["data"]
