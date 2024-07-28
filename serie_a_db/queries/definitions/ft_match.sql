CREATE TABLE IF NOT EXISTS ft_match (
    match_day_id STR NOT NULL,
    home_team_id STR NOT NULL,
    away_team_id STR NOT NULL,
    home_coach_id STR NOT NULL,
    away_coach_id STR NOT NULL,
    code_serie_a_api INT NOT NULL,
    home_goals INT NOT NULL CHECK (home_goals >= 0),
    home_penalty_goals INT NOT NULL CHECK (home_penalty_goals >= 0),
    home_schema STR NOT NULL,
    away_goals INT NOT NULL CHECK (away_goals >= 0),
    away_penalty_goals INT NOT NULL CHECK (away_penalty_goals >= 0),
    away_schema STR NOT NULL,
    status STR NOT NULL CHECK (status IN ("completed", "ongoing", "upcoming")),
    date STR NOT NULL CHECK (date = strftime('%Y-%m-%d', date)),
    time STR NOT NULL CHECK (time = strftime('%H:%M:%S', time)),
    time_zone STR NOT NULL CHECK (time_zone IN ("UTC+2")),
    duration_minutes INT CHECK (
        duration_minutes BETWEEN 0 AND 120
    ),
    PRIMARY KEY (match_day_id, home_team_id),
    FOREIGN KEY (match_day_id) REFERENCES dm_match_day (match_day_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (home_team_id) REFERENCES dm_team (team_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (away_team_id) REFERENCES dm_team (team_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (home_coach_id) REFERENCES dm_coach (coach_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (away_coach_id) REFERENCES dm_coach (coach_id) ON UPDATE CASCADE ON DELETE RESTRICT
);


INSERT INTO ft_match
SELECT stm.match_day_id,
    stm.home_team_id,
    stm.away_team_id,
    dmc_home.coach_id AS home_coach_id,
    dmc_away.coach_id AS away_coach_id,
    stm.match_code_serie_a_api AS code_serie_a_api,
    stm.home_goals,
    stm.home_penalty_goals,
    stm.home_schema,
    stm.away_goals,
    stm.away_penalty_goals,
    stm.away_schema,
    stm.status,
    stm.date,
    stm.time,
    stm.time_zone,
    stm.duration_minutes
FROM st_match AS stm
    INNER JOIN dm_coach AS dmc_home ON (
        stm.home_coach_name = dmc_home.name
        AND stm.home_coach_surname = dmc_home.surname
    )
    INNER JOIN dm_coach AS dmc_away ON (
        stm.away_coach_name = dmc_away.name
        AND stm.away_coach_surname = dmc_away.surname
    )
WHERE TRUE ON CONFLICT (match_day_id, home_team_id) DO
UPDATE
SET away_team_id = EXCLUDED.away_team_id,
    home_coach_id = EXCLUDED.home_coach_id,
    away_coach_id = EXCLUDED.away_coach_id,
    code_serie_a_api = EXCLUDED.code_serie_a_api,
    home_goals = EXCLUDED.home_goals,
    home_penalty_goals = EXCLUDED.home_penalty_goals,
    home_schema = EXCLUDED.home_schema,
    away_goals = EXCLUDED.away_goals,
    away_penalty_goals = EXCLUDED.away_penalty_goals,
    away_schema = EXCLUDED.away_schema,
    status = EXCLUDED.status,
    date = EXCLUDED.date,
    time = EXCLUDED.time,
    time_zone = EXCLUDED.time_zone,
    duration_minutes = EXCLUDED.duration_minutes;