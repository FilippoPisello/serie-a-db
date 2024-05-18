from unittest.mock import Mock

from serie_a_db.data_extraction.table_specific_extractors.dm_match_day import (
    scrape_match_day_data,
)


def test_scraping_match_day_data(db):
    # Arrange
    serie_a_client = Mock()
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

    db.execute("CREATE TABLE dm_season (code_serie_a_api INT)")
    db.execute("INSERT INTO dm_season (code_serie_a_api) VALUES (123)")

    # Act
    data = scrape_match_day_data(db, serie_a_client)

    # Assert
    assert data == [
        (123, 157707, 1, "completed"),
        (123, 157713, 21, "upcoming"),
    ]


def test_scraping_match_day_no_season_table(db):
    # Arrange
    serie_a_client = Mock()
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
    assert data == []


def test_scraping_match_day_empty_season_table(db):
    # Arrange
    serie_a_client = Mock()
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

    db.execute("CREATE TABLE dm_season (code_serie_a_api INT)")

    # Act
    data = scrape_match_day_data(db, serie_a_client)

    # Assert
    assert data == []
