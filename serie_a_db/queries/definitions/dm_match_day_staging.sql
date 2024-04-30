CREATE TABLE dm_match_day_staging (
    season_id STR NOT NULL,
    code_serie_a_api INT NOT NULL,
    number INT NOT NULL CHECK (number IN (1, 38)),
    active INT DEFAULT 0 CHECK (active IN (0, 1))
);
