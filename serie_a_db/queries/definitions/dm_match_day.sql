CREATE TABLE IF NOT EXISTS dm_match_day (
    match_day_id STR PRIMARY KEY CHECK (LENGTH(match_day_id) = 6),
    season_id STR,
    display_name STR NOT NULL,
    code_serie_a_api INT NOT NULL,
    number INT NOT NULL CHECK (
        number BETWEEN 1 AND 38
    ),
    status STR CHECK (status IN ("completed", "ongoing", "upcoming")),
    FOREIGN KEY (season_id) REFERENCES dm_season (season_id) ON UPDATE CASCADE ON DELETE RESTRICT
);


WITH dm_match_day_preload AS (
    SELECT dses.season_id AS season_id,
        dses.season_id || 'M' || SUBSTR('0' || dmds.number, -2) AS match_day_id,
        dses.display_name || ' MD' || SUBSTR('0' || dmds.number, -2) AS display_name,
        dmds.code_serie_a_api AS code_serie_a_api,
        dmds.number AS number,
        dmds.status AS status
    FROM st_match_day AS dmds
        INNER JOIN dm_season AS dses ON (
            dmds.season_code_serie_a_api = dses.code_serie_a_api
        )
)
INSERT INTO dm_match_day
SELECT match_day_id,
    season_id,
    display_name,
    code_serie_a_api,
    number,
    status
FROM dm_match_day_preload
WHERE TRUE ON CONFLICT (match_day_id) DO
UPDATE
SET season_id = EXCLUDED.season_id,
    display_name = EXCLUDED.display_name,
    code_serie_a_api = EXCLUDED.code_serie_a_api,
    number = EXCLUDED.number,
    status = EXCLUDED.status;