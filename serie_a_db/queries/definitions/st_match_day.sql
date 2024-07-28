CREATE TABLE st_match_day (
    season_code_serie_a_api STR NOT NULL,
    season_year_start INT NOT NULL CHECK (season_year_start BETWEEN 1980 AND 2050),
    code_serie_a_api INT NOT NULL,
    number INT NOT NULL CHECK (number BETWEEN 1 AND 38),
    status STR NOT NULL CHECK (status IN ("completed", "ongoing", "upcoming"))
    PRIMARY KEY (season_year_start, number)
);
