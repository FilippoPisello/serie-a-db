CREATE TABLE IF NOT EXISTS dm_coach (
    coach_id STR PRIMARY KEY CHECK (LENGTH(coach_id) = 9),
    code_serie_a_api INT NOT NULL,
    name STR,
    surname STR NOT NULL
);


WITH dm_coach_preload AS (
    SELECT DISTINCT home_coach_code_serie_a_api AS code_serie_a_api,
        home_coach_name AS name,
        home_coach_surname AS surname
    FROM st_match
    UNION
    SELECT DISTINCT away_coach_code_serie_a_api AS code_serie_a_api,
        away_coach_name AS name,
        away_coach_surname AS surname
    FROM st_match
)
INSERT INTO dm_coach
SELECT UPPER(
        SUBSTR(
            REPLACE(REPLACE(name, ' ', ''), '''', '') || '0000',
            1,
            4
        ) || '-' || SUBSTR(
            REPLACE(REPLACE(surname, ' ', ''), '''', '') || '0000',
            1,
            4
        )
    ) AS coach_id,
    code_serie_a_api,
    name,
    surname
FROM dm_coach_preload
WHERE TRUE ON CONFLICT (coach_id) DO
UPDATE
SET code_serie_a_api = EXCLUDED.code_serie_a_api,
    name = EXCLUDED.name,
    surname = EXCLUDED.surname;