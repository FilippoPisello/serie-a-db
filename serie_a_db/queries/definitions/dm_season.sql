CREATE TABLE IF NOT EXISTS dm_season (
    season_id STR PRIMARY KEY,
    label STR NOT NULL,
    year_start INT NOT NULL,
    year_end INT NOT NULL,
    active INT DEFAULT 0 CHECK (active IN (0, 1))
);