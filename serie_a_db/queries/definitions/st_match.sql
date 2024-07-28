CREATE TABLE st_match (
    match_day_id STR NOT NULL CHECK (LENGTH(match_day_id) = 6),
    match_code_serie_a_api INT NOT NULL,
    home_team_id STR NOT NULL CHECK (LENGTH(home_team_id) = 3),
    home_team_name STR NOT NULL,
    home_goals INT NOT NULL CHECK (home_goals >= 0),
    home_penalty_goals INT NOT NULL CHECK (home_penalty_goals >= 0),
    home_schema STR NOT NULL,
    home_coach_code_serie_a_api INT NOT NULL,
    home_coach_name STR NOT NULL,
    home_coach_surname STR NOT NULL,
    away_team_id STR NOT NULL CHECK (LENGTH(away_team_id) = 3),
    away_team_name STR NOT NULL,
    away_goals INT NOT NULL CHECK (away_goals >= 0),
    away_penalty_goals INT NOT NULL CHECK (away_penalty_goals >= 0),
    away_schema STR NOT NULL,
    away_coach_code_serie_a_api INT NOT NULL,
    away_coach_name STR NOT NULL,
    away_coach_surname STR NOT NULL,
    STATUS STR NOT NULL CHECK (STATUS IN ("completed", "ongoing", "upcoming")),
    date STR NOT NULL CHECK (date = strftime('%Y-%m-%d', date)),
    time STR NOT NULL CHECK (time = strftime('%H:%M:%S', time)),
    time_zone STR NOT NULL CHECK (time_zone IN ("UTC+2")),
    duration_minutes INT CHECK (
        duration_minutes BETWEEN 0 AND 120
    ),
    PRIMARY KEY (match_day_id, home_team_id),
    FOREIGN KEY (match_day_id) REFERENCES dm_match_day (match_day_id) ON UPDATE CASCADE ON DELETE RESTRICT
);