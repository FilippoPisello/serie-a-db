CREATE TABLE st_fpi_player_match (
    match_day_id STR NOT NULL CHECK (LENGTH(match_day_id) = 6),
    team_name STR NOT NULL,
    name STR NOT NULL,
    code_fpi INT NOT NULL,
    role STR NOT NULL CHECK (role IN ("G", "D", "M", "A")),
    fantacalcio_punto_it_grade FLOAT NOT NULL CHECK (
        fantacalcio_punto_it_grade BETWEEN 0 AND 10
    ),
    fantacalcio_punto_it_fanta_grade FLOAT NOT NULL,
    italia_grade FLOAT NOT NULL CHECK(
        italia_grade BETWEEN 0 AND 10
    ),
    italia_fanta_grade FLOAT NOT NULL,
    statistical_grade FLOAT NOT NULL CHECK(
        statistical_grade BETWEEN 0 AND 10
    ),
    statistical_fanta_grade FLOAT NOT NULL,
    goals_scored INT NOT NULL CHECK (goals_scored >= 0),
    goals_conceded INT NOT NULL CHECK (goals_conceded >= 0),
    own_goals INT NOT NULL CHECK (own_goals >= 0),
    penalties_scored INT NOT NULL CHECK (penalties_scored >= 0),
    penalties_missed INT NOT NULL CHECK (penalties_missed >= 0),
    penalties_saved INT NOT NULL CHECK (penalties_saved >= 0),
    assists INT NOT NULL CHECK (assists >= 0),
    yellow_card INT NOT NULL CHECK (yellow_card IN (0, 1)),
    red_card INT NOT NULL CHECK (red_card IN (0, 1)),
    subbed_in INT NOT NULL CHECK (subbed_in IN (0, 1)),
    subbed_out INT NOT NULL CHECK (subbed_out IN (0, 1)),
    PRIMARY KEY (match_day_id, team_name, code_fpi),
    FOREIGN KEY (match_day_id) REFERENCES dm_match_day (match_day_id) ON UPDATE CASCADE ON DELETE RESTRICT
);