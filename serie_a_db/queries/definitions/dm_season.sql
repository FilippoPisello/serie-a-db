CREATE TABLE IF NOT EXISTS dm_season (
    season_id STR PRIMARY KEY CHECK (LENGTH(season_id) = 3),
    display_name STR NOT NULL CHECK (LENGTH(display_name) = 6),
    code_serie_a_api INT NOT NULL,
    year_start INT NOT NULL CHECK (
        year_start BETWEEN 1980 AND 2050
    ),
    year_end INT NOT NULL CHECK (
        year_end BETWEEN 1980 AND 2050
    ),
    STATUS STR CHECK (STATUS IN ("completed", "ongoing", "upcoming")),
    CHECK (year_end = year_start + 1)
);


WITH dm_season_enriched AS (
    SELECT season_code_serie_a_api AS code_serie_a_api,
        season_year_start AS year_start,
        SUBSTR(season_year_start, 3, 2) AS year_start_yy,
        SUBSTR(season_year_start + 1, 3, 2) AS year_end_yy,
        GROUP_CONCAT(DISTINCT STATUS) AS statuses
    FROM st_match_day
    GROUP BY season_code_serie_a_api,
        season_year_start
),
dm_season_preload AS (
    SELECT 'S' || year_start_yy AS season_id,
        'S' || year_start_yy || '-' || year_end_yy AS display_name,
        code_serie_a_api AS code_serie_a_api,
        year_start AS year_start,
        year_start + 1 AS year_end,
        CASE
            WHEN statuses = 'completed' THEN 'completed'
            WHEN statuses = 'upcoming' THEN 'upcoming'
            ELSE 'ongoing'
        END AS STATUS
    FROM dm_season_enriched
)
INSERT INTO dm_season
SELECT season_id,
    display_name,
    code_serie_a_api,
    year_start,
    year_end,
    STATUS
FROM dm_season_preload
WHERE TRUE ON CONFLICT (season_id) DO
UPDATE
SET display_name = EXCLUDED.display_name,
    code_serie_a_api = EXCLUDED.code_serie_a_api,
    year_start = EXCLUDED.year_start,
    year_end = EXCLUDED.year_end,
    STATUS = EXCLUDED.status;