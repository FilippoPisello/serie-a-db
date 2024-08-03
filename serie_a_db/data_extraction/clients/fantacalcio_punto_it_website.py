"""Get data from the website Fantacalcio.it."""

import requests


class FantacalcioPuntoItWebsite:
    """Client to request data from the Fantacalcio.it website."""

    ROOT = "https://www.fantacalcio.it"

    @classmethod
    def get_grades_page(cls, season_year_start: int, match_day_number: int) -> str:
        """Get the raw HTML of the grades page."""
        # Season tag is in the format "2021-22"
        season_tag = f"{season_year_start}-{str(season_year_start + 1)[2:]}"
        url = f"{cls.ROOT}/voti-fantacalcio-serie-a/{season_tag}/{match_day_number}"
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        return resp.text
