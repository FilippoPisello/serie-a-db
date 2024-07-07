CREATE TABLE IF NOT EXISTS dm_team (
    team_id STR PRIMARY KEY CHECK (LENGTH(team_id) = 3),
    name STR NOT NULL
);

WITH dm_team_preload AS (
    SELECT DISTINCT
        UPPER(home_team_id) AS team_id,
        -- Get the latest name of the team
        MIN(home_team_name) OVER
            (PARTITION BY home_team_id) AS name
    FROM st_match)
INSERT INTO dm_team
SELECT
    team_id,
    name
FROM dm_team_preload
WHERE true
ON CONFLICT (team_id) DO UPDATE
SET
    name = EXCLUDED.name
;
