from unittest.mock import Mock

from serie_a_db.db.db import Db
from serie_a_db.db.update_tables import CoreTable, StagingTable
from serie_a_db.db.update_tables.tables.dm_season import (
    Season,
    scrape_data_from_the_web,
)


def test_dm_season_update(db: Db):
    """Test the update method of DmSeason."""
    # Arrange
    dm_season = CoreTable.from_file("dm_season")
    data = [
        Season(year_start=2023, code_serie_a_api=23, active=1).to_namedtuple(),
        Season(year_start=2022, code_serie_a_api=22, active=0).to_namedtuple(),
    ]
    dm_staging = StagingTable.from_file("dm_season_staging", lambda: data)

    # Act
    dm_staging.update(db)
    dm_season.update(db)

    # Assert
    assert db.count_rows("dm_season") == len(data)
    assert db.get_all_rows("dm_season") == [
        ("23-24", "S23-24", 23, 2023, 2024, 1),
        ("22-23", "S22-23", 22, 2022, 2023, 0),
    ]


class TestExtractData:
    """Test the logic within the extract_data method of DmSeason."""

    @staticmethod
    def test_seasons_scraping():
        mock_client = Mock()
        mock_client.get_homepage.return_value = r"""
        <div class="whatever">
            <select class="hm-select" name="season" dir="rtl">
                <option value="157617" selected="">2023-24</option>
                <option value="150052">2022-23</option>
            </select>
        </div>
        """
        mock_client.get_season_page.return_value = {
            "data": [
                {
                    "id_category": 157707,
                    "title": "1° Giornata ",
                    "category_status": "PLAYED",
                },
                {
                    "id_category": 157713,
                    "title": "2° Giornata ",
                    "category_status": "PLAYED",
                },
            ],
        }

        data = scrape_data_from_the_web(mock_client, min_season=2000)

        assert data == [
            (2023, 157617, 0),
            (2022, 150052, 0),
        ]

    @staticmethod
    def test_seasons_earlier_than_earliest_year_are_ignored():
        mock_client = Mock()
        mock_client.get_homepage.return_value = r"""
        <div class="whatever">
            <select class="hm-select" name="season" dir="rtl">
                <option value="157617" selected="">1999-00</option>
                <option value="150052">2000-01</option>
            </select>
        </div>
        """
        mock_client.get_season_page.return_value = {
            "data": [
                {
                    "id_category": 157707,
                    "title": "1° Giornata ",
                    "category_status": "PLAYED",
                },
                {
                    "id_category": 157713,
                    "title": "2° Giornata ",
                    "category_status": "PLAYED",
                },
            ],
        }

        data = scrape_data_from_the_web(mock_client, min_season=2000)

        assert data == [
            (2000, 150052, 0),
        ]
