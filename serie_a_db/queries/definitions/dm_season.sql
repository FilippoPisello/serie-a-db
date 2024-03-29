CREATE TABLE IF NOT EXISTS dm_season (
    season_id STR PRIMARY KEY,
    display_name STR NOT NULL,
    code_serie_a_api INT NOT NULL,
    year_start INT NOT NULL CHECK (BETWEEN 1980 AND 2050),
    year_end INT NOT NULL (BETWEEN 1980 AND 2050),
    active INT DEFAULT 0 CHECK (active IN (0, 1)),
    CHECK (year_end = year_start + 1)
);

CREATE TABLE dm_season_staging (
    year_start INT NOT NULL CHECK (BETWEEN 1980 AND 2050),
    code_serie_a_api INT NOT NULL,
    active INT DEFAULT 0 CHECK (active IN (0, 1))
);

WITH dm_season_preload AS (
    SELECT
        SUBSTR(year_start, 3, 2)
            || '-'
            || SUBSTR(year_start + 1, 3, 2) AS season_id,
        'S'
            || season_id                    AS display_name,
        code_serie_a_api                    AS code_serie_a_api,
        year_start                          AS year_start,
        year_start + 1                      AS year_end,
        active                              AS active
)
INSERT INTO dm_season
SELECT
    season_id,
    display_name,
    code_serie_a_api,
    year_start,
    year_end,
    active
FROM dm_season_preload
WHERE true
ON CONFLICT (season_id) DO UPDATE
SET
    display_name = EXCLUDED.display_name,
    code_serie_a_api = EXCLUDED.code_serie_a_api,
    year_start = EXCLUDED.year_start,
    year_end = EXCLUDED.year_end,
    active = EXCLUDED.active
;
