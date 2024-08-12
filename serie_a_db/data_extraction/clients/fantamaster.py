"""Get data from the Fantamaster website."""

import requests


class FantamasterWebsite:
    """Client to request data from the Fantamaster website."""

    ROOT_API = "https://apicdn.fantamaster.it"

    @classmethod
    def get_players(cls) -> list[dict]:
        """Return a list of players data, each represented as a dict."""
        resp = requests.get(cls.ROOT_API + "/playersstats/", timeout=5)
        resp.raise_for_status()
        return resp.json()["players"]
