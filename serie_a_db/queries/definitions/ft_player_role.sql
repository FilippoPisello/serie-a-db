CREATE TABLE IF NOT EXISTS ft_player_role (
    player_id INT NOT NULL,
    season_id INT NOT NULL,
    data_source_id STR NOT NULL,
    role STR NOT NULL CHECK (role IN ('G', 'D', 'M', 'A')),
    PRIMARY KEY (player_id, season_id, data_source_id),
    FOREIGN KEY (player_id) REFERENCES dm_player (player_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (season_id) REFERENCES dm_season (season_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (data_source_id) REFERENCES dm_data_source (data_source_id) ON UPDATE CASCADE ON DELETE RESTRICT
);


WITH fpi_data AS (
    SELECT DISTINCT stfpm.code_fpi AS player_id,
        dmmd.season_id,
        'FPI' AS data_source_id,
        stfpm.role
    FROM st_fpi_player_match AS stfpm
        INNER JOIN dm_match_day AS dmmd ON stfpm.match_day_id = dmmd.match_day_id
    UNION ALL
    SELECT code_fpi AS player_id,
        season_id,
        'FPI' AS data_source_id,
        role
    FROM st_fpi_player
    WHERE load_ts = (
            SELECT MAX(load_ts)
            FROM st_fpi_player
        )
),
fm_data AS (
    SELECT DISTINCT code_fm AS player_id,
        season_id,
        'FM' AS data_source_id,
        role,
        ROW_NUMBER() OVER (
            PARTITION BY code_fm,
            season_id
            ORDER BY load_ts DESC
        ) AS rn
    FROM st_fm_player
),
ft_player_role_preload AS (
    SELECT player_id,
        season_id,
        data_source_id,
        role
    FROM fpi_data
    UNION ALL
    SELECT player_id,
        season_id,
        data_source_id,
        role
    FROM fm_data
    WHERE rn = 1
)
INSERT INTO ft_player_role
SELECT player_id,
    season_id,
    data_source_id,
    role
FROM ft_player_role_preload
WHERE TRUE ON CONFLICT (player_id, season_id, data_source_id) DO
UPDATE
SET role = EXCLUDED.role;