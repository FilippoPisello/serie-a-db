from serie_a_db import DEFINITIONS_DIR
from serie_a_db.data_extraction.table_specific_extractors.st_match import (
    Match,
    api_response_to_match_object,
)
from serie_a_db.sql_parsing import extract_attributes_from_create_statement


def test_raw_serie_a_api_response_should_be_converted_to_custom_object():
    match = {
        "away_coach_id": 10,
        "away_coach_image": "https://img.legaseriea.it/vimages/632c8cbe/GSPGP.png",
        "away_coach_name": "GIAN PIERO",
        "away_coach_surname": "GASPERINI",
        "away_goal": 2,
        "away_netco_id": "ATALAN",
        "away_penalty_goal": 0,
        "away_schema": "3 - 4 - 1 - 2",
        "away_secondary_team_logo": "https://img.legaseriea.it/vimages/62cfd69d/atalanta.png",
        "away_team_active": 1,
        "away_team_logo": "https://img.legaseriea.it/vimages/62cfd69d/atalanta.png",
        "away_team_name": "ATALANTA",
        "away_team_short_name": "ATA",
        "away_team_url": "/team/atalanta",
        "broadcasters": "[]",
        "category_status": None,
        "championship_background_image": "https://img.legaseriea.it/vimages/62cd7ae3/type=9.png",
        "championship_category_id": 150060,
        "championship_category_status": "",
        "championship_image": "https://img.legaseriea.it/vimages/632899a6/SerieA_TIM_RGB.jpg",
        "championship_metadata": "[]",
        "championship_title": "SERIE A",
        "date_time": "2022-08-13T16:30:00Z",
        "georule_id": 1,
        "highlight": "/media/serie-a/sampdoria-0-2-atalanta-12lk8e1h2j5d90",
        "home_coach_id": 125,
        "home_coach_image": "https://img.legaseriea.it/vimages/63340b74/MRGMP.png",
        "home_coach_name": "MARCO",
        "home_coach_surname": "GIAMPAOLO",
        "home_goal": 0,
        "home_netco_id": "SAMP",
        "home_penalty_goal": 0,
        "home_schema": "4 - 4 - 1 - 1",
        "home_secondary_team_logo": "https://img.legaseriea.it/vimages/62cef574/sampdoria.png",
        "home_team_active": 0,
        "home_team_logo": "https://img.legaseriea.it/vimages/62cef574/sampdoria.png",
        "home_team_name": "SAMPDORIA",
        "home_team_short_name": "SAM",
        "home_team_ticket_url": "https://www.sampdoria.it/biglietteria/",
        "home_team_url": "/team/sampdoria",
        "id_category": 150052,
        "live_timing": "51'38",
        "match_day_category_status": "PLAYED",
        "match_day_id_category": 150194,
        "match_day_title": "Match Day 1",
        "match_hm": "18:30:00",
        "match_id": 166914,
        "match_lineup_pdf": "",
        "match_name": "SAMPDORIA VS ATALANTA",
        "match_program_pdf": "https://img.legaseriea.it/vimages/631f1f1d/2022-23_A_UNICO_UNI_1_SAMATA_ENG.pdf",
        "match_report": 1,
        "match_report_pdf": "https://img.legaseriea.it/vimages/63288972/2022-23_A_UNICO_UNI_1_SAMATA_ENG.pdf",
        "match_status": 2,
        "minutes_played": "98'53",
        "netco_id": "SAMATA",
        "play_phase": "2T",
        "referee": "FEDERICO DIONISI",
        "round_category_status": None,
        "round_id_category": 150155,
        "round_title": " UNICO",
        "season_title": "2022-23",
        "slug": "/match/sampdoria-atalanta-166914",
        "ticket_url": "https://www.sampdoria.it/biglietteria/",
        "unknown_datetime": 0,
        "venue_background_image": "https://img.legaseriea.it/vimages/64a2c8bb/IMG_3486.jpg",
        "venue_id": 30345,
        "venue_image": "https://img.legaseriea.it/vimages/64a2c8bb/IMG_3486.jpg",
        "venue_name": "LUIGI FERRARIS",
        "venue_plan_image": "https://img.legaseriea.it/vimages/64a2c935/piantastadio.jpg",
        "weather": "",
    }

    # Act
    actual = api_response_to_match_object("S24M01", match)

    # Assert
    actual.assert_equal(
        Match(
            match_day_id="S24M01",
            match_code_serie_a_api=166914,
            away_team_id="ATA",
            away_team_name="Atalanta",
            home_team_id="SAM",
            home_team_name="Sampdoria",
            away_goals=2,
            away_penalty_goals=0,
            home_goals=0,
            home_penalty_goals=0,
            away_schema="3-4-1-2",
            home_schema="4-4-1-1",
            duration_minutes=99,
            date="2022-08-13",
            time="18:30:00",
            time_zone="UTC+2",
            status="completed",
            away_coach_code_serie_a_api=10,
            away_coach_name="Gian Piero",
            away_coach_surname="Gasperini",
            home_coach_code_serie_a_api=125,
            home_coach_name="Marco",
            home_coach_surname="Giampaolo",
        )
    )


def test_query_and_object_are_compatible():
    query = DEFINITIONS_DIR / "st_match.sql"

    query_attr = extract_attributes_from_create_statement(query.read_text())
    model_attr = Match.fields()

    assert query_attr == model_attr
