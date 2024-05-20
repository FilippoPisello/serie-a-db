CREATE TABLE st_match (
    match_day_id STR NOT NULL CHECK (LENGTH(match_day_id) = 6),
    match_code_serie_a_api INT NOT NULL,
    away_team_id STR NOT NULL CHECK (LENGTH(away_team_id) = 3),
    away_team_name STR NOT NULL,
    home_team_id STR NOT NULL CHECK (LENGTH(home_team_id) = 3),
    home_team_name STR NOT NULL,
    away_goals INT NOT NULL CHECK (away_goals >= 0),
    away_penalty_goals INT NOT NULL CHECK (away_penalty_goals >= 0),
    home_goals INT NOT NULL CHECK (home_goals >= 0),
    home_penalty_goals INT NOT NULL CHECK (home_penalty_goals >= 0),
    away_schema STR NOT NULL,
    home_schema STR NOT NULL,
    duration_minutes INT NOT NULL CHECK (duration_minutes BETWEEN 0 AND 120),
    date STR NOT NULL CHECK (date = strftime('%Y-%m-%d', date)),
    time STR NOT NULL CHECK (time = strftime('%H:%M:%f', time)),
    status STR NOT NULL CHECK (status IN ("completed", "ongoing", "upcoming")),
    away_coach_code_serie_a_api INT NOT NULL,
    away_coach_name STR NOT NULL,
    away_coach_surname STR NOT NULL,
    home_coach_code_serie_a_api INT NOT NULL,
    home_coach_name STR NOT NULL,
    home_coach_surname STR NOT NULL,
    FOREIGN KEY (match_day_id)
        REFERENCES dm_match_day (match_day_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);
