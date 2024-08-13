CREATE TABLE st_player_cross_source_mapping (
    season_id STR NOT NULL,
    code_fpi INT NOT NULL,
    code_fm INT NOT NULL,
    PRIMARY KEY (season_id, code_fpi),
    FOREIGN KEY (season_id) REFERENCES dm_season (season_id) ON UPDATE CASCADE ON DELETE RESTRICT
)