CREATE TABLE st_fpi_player (
    load_ts STR CHECK (
        load_ts = strftime('%Y-%m-%d %H:%M:%f', load_ts)
    ),
    season_id STR NOT NULL,
    team_id STR NOT NULL,
    name STR NOT NULL,
    code_fpi INT NOT NULL,
    role STR NOT NULL CHECK (role IN ("G", "D", "M", "A")),
    price_initial INT NOT NULL,
    price_current FLOAT NOT NULL,
    PRIMARY KEY (load_ts, code),
    FOREIGN KEY (season_id) REFERENCES dm_season (season_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (team_id) REFERENCES dm_team (team_id) ON UPDATE CASCADE ON DELETE RESTRICT
);