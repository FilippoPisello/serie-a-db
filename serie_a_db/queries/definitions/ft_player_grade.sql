CREATE TABLE IF NOT EXISTS ft_player_grade (
    match_day_id STR NOT NULL,
    player_id INT NOT NULL,
    data_source_id STR NOT NULL,
    grade FLOAT NOT NULL,
    PRIMARY KEY (match_day_id, player_id, data_source_id),
    FOREIGN KEY (match_day_id) REFERENCES dm_match_day (match_day_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (player_id) REFERENCES dm_player (player_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (data_source_id) REFERENCES dm_data_source (data_source_id) ON UPDATE CASCADE ON DELETE RESTRICT
);


WITH preload AS (
    SELECT match_day_id,
        code_fpi AS player_id,
        'FPI' AS data_source_id,
        fantacalcio_punto_it_grade AS grade
    FROM st_fpi_player_match
    UNION ALL
    SELECT match_day_id,
        code_fpi AS player_id,
        'ITA' AS data_source_id,
        italia_grade AS grade
    FROM st_fpi_player_match
    UNION ALL
    SELECT match_day_id,
        code_fpi AS player_id,
        'ST' AS data_source_id,
        statistical_grade AS grade
    FROM st_fpi_player_match
)
INSERT INTO ft_player_grade
SELECT match_day_id,
    player_id,
    data_source_id,
    grade
FROM preload
WHERE TRUE ON CONFLICT (match_day_id, player_id, data_source_id) DO
UPDATE
SET grade = EXCLUDED.grade;