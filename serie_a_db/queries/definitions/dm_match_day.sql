CREATE TABLE IF NOT EXISTS dm_match_day (
    match_day_id STR PRIMARY KEY,
    season_id STR,
    display_name STR NOT NULL,
    code_serie_a_api INT NOT NULL,
    number INT NOT NULL CHECK (number IN (1, 38)),
    active INT DEFAULT 0 CHECK (active IN (0, 1))
);

CREATE TABLE dm_match_day_staging (
    season_starting_year INT NOT NULL,
    code_serie_a_api INT NOT NULL,
    number INT NOT NULL CHECK (number IN (1, 38)),
    active INT DEFAULT 0 CHECK (active IN (0, 1))
);

WITH dm_match_day_preload AS (
    SELECT
        SUBSTR(season_starting_year, 3, 2)
            || '-'
            || SUBSTR(season_starting_year + 1, 3, 2) AS season_id,
        season_id
            || '-'
            || LPAD(number, 2, '0')                   AS match_day_id,
        SUBSTR(season_starting_year, 3, 2)
            || '/'
            || SUBSTR(season_starting_year + 1, 3, 2)
            || ' MD'
            || number                                 AS display_name,
        code_serie_a_api                              AS code_serie_a_api,
        number                                        AS number,
        active                                        AS active
    FROM dm_match_day_staging
)
INSERT INTO dm_match_day
SELECT
    match_day_id,
    season_id,
    display_name,
    code_serie_a_api,
    number,
    active
FROM dm_match_day_preload
ON CONFLICT (match_day_id) DO UPDATE
SET season_id = EXCLUDED.season_id,
    display_name = EXCLUDED.display_name,
    code_serie_a_api = EXCLUDED.code_serie_a_api,
    number = EXCLUDED.number,
    active = EXCLUDED.active
;
