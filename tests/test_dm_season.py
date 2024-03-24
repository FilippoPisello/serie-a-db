from unittest.mock import Mock

from serie_a_db.update.dm_season import DmSeason


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
    updater = DmSeason(db=None, script=None)
    updater.SERIE_A_WEBSITE = mock_client
    data = updater.extract_data()
    assert data == [
        (2023, 157617, 0),
        (2022, 150052, 0),
    ]


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
    updater = DmSeason(db=None, script=None)
    updater.SERIE_A_WEBSITE = mock_client
    updater.EARLIEST_SEASON = 2000

    data = updater.extract_data()

    assert data == [
        (2000, 150052, 0),
    ]
