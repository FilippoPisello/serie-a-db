CREATE TABLE dm_match_day_staging (
    season_code_serie_a_api STR NOT NULL,
    code_serie_a_api INT NOT NULL,
    number INT NOT NULL CHECK (number BETWEEN 1 AND 38),
    status STR NOT NULL CHECK (status IN ("completed", "ongoing", "upcoming"))
);
