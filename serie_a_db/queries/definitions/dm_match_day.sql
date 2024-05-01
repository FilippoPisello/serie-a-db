CREATE TABLE IF NOT EXISTS dm_match_day (
    match_day_id STR PRIMARY KEY,
    season_id STR,
    display_name STR NOT NULL,
    code_serie_a_api INT NOT NULL,
    number INT NOT NULL CHECK (number IN (1, 38)),
    status STR CHECK (status IN ("completed", "ongoing", "upcoming"))
);


WITH dm_match_day_preload AS (
    SELECT
        dses.season_id                                AS season_id,
        dses.season_id
            || 'M'
            || dmds.number                            AS match_day_id,
        dses.display_name
            || ' MD'
            || number                                 AS display_name,
        code_serie_a_api                              AS code_serie_a_api,
        number                                        AS number,
        active                                        AS active
    FROM dm_match_day_staging AS dmds
        INNER JOIN dm_season AS dses
            ON (dmds.season_code_serie_a_api = dses.season_code_serie_a_api)
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
