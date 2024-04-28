CREATE TABLE dm_season_staging (
    year_start INT NOT NULL CHECK (year_start BETWEEN 1980 AND 2050),
    code_serie_a_api INT NOT NULL,
    active INT DEFAULT 0 CHECK (active IN (0, 1))
);
