import requests


class SerieAWebsite:
    ROOT = "https://www.legaseriea.it"

    @classmethod
    def get_homepage(cls) -> str:
        resp = requests.get(f"{cls.ROOT}/en/serie-a", timeout=5)
        resp.raise_for_status()
        return resp.text

    @classmethod
    def get_season_page(cls, season_api_code: int) -> dict:
        resp = requests.get(
            f"{cls.ROOT}/api/season/{season_api_code}/championship/A/matchday?lang=eng",
            timeout=5,
        )
        resp.raise_for_status()
        return resp.json()
