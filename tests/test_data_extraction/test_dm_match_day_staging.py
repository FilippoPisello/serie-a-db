from unittest.mock import Mock

from serie_a_db.data_extraction.table_specific_extractors.dm_match_day import (
    scrape_match_day_data,
)


def test_scraping_match_day_data(db):
    # Arrange
    serie_a_client = Mock()
    serie_a_client.get_homepage.return_value = r"""
    <div class="whatever">
        <select class="hm-select" name="season" dir="rtl">
            <option value="157617" selected="">2023-24</option>
        </select>
    </div>"""
    serie_a_client.get_season_page.return_value = {
        "data": [
            {
                "id_category": 157707,
                "title": "1° Giornata ",
                "description": "1",
                "category_status": "PLAYED",
            },
            {
                "id_category": 157713,
                "title": "21° Giornata ",
                "description": "21",
                "category_status": "TO BE PLAYED",
            },
        ],
    }

    # Act
    data = scrape_match_day_data(db, serie_a_client)

    # Assert
    assert data == [
        (157617, 2023, 157707, 1, "completed"),
        (157617, 2023, 157713, 21, "upcoming"),
    ]


def test_seasons_earlier_than_earliest_year_are_ignored(db):
    # Arrange
    serie_a_client = Mock()
    serie_a_client.get_homepage.return_value = r"""
    <div class="whatever">
        <select class="hm-select" name="season" dir="rtl">
            <option value="157617" selected="">1999-00</option>
            <option value="150052">2000-01</option>
        </select>
    </div>
    """
    serie_a_client.get_season_page.return_value = {
        "data": [
            {
                "id_category": 157707,
                "title": "1° Giornata ",
                "description": "1",
                "category_status": "PLAYED",
            },
        ],
    }
    earliest_season = 2000
    # db.execute("CREATE OR REPLACE TABLE params (key TEXT PRIMARY KEY, value TEXT)")
    # db.execute("INSERT INTO params VALUES ('earliest_season', '2000')")

    # Act
    data = scrape_match_day_data(db, serie_a_client, earliest_season)

    # Assert
    assert all(row.season_year_start >= earliest_season for row in data)
