CREATE TABLE IF NOT EXISTS dm_player (
    player_id INTEGER PRIMARY KEY,
    name STR NOT NULL
);


WITH dm_player_preload AS (
    SELECT DISTINCT code_fpi AS player_id,
        name
    FROM st_fpi_player_match
    UNION ALL
    SELECT DISTINCT code_fpi AS player_id,
        name
    FROM st_fpi_player
)
INSERT INTO dm_player
SELECT player_id,
    name
FROM dm_player_preload
WHERE TRUE ON CONFLICT (player_id) DO
UPDATE
SET name = EXCLUDED.name;