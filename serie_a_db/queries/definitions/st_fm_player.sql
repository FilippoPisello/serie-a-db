CREATE TABLE st_fm_player (
    load_ts STR CHECK (
        load_ts = strftime('%Y-%m-%d %H:%M:%f', load_ts)
    ),
    season_id STR NOT NULL,
    team_id STR NULL,
    code_fm INT NOT NULL,
    name STR NOT NULL,
    role STR NOT NULL CHECK (role IN ("G", "D", "M", "A")),
    value INT NOT NULL CHECK (value > 0),
    PRIMARY KEY (load_ts, code_fm),
    FOREIGN KEY (season_id) REFERENCES dm_season (season_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (team_id) REFERENCES dm_team (team_id) ON UPDATE CASCADE ON DELETE RESTRICT
);