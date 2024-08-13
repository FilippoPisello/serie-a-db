CREATE TABLE IF NOT EXISTS ft_player_match (
    match_day_id STR NOT NULL,
    player_id INT NOT NULL,
    team_id STR NOT NULL,
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
    fanta_bonus_total FLOAT NOT NULL,
    PRIMARY KEY (match_day_id, player_id, team_id),
    FOREIGN KEY (match_day_id) REFERENCES dm_match_day (match_day_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (player_id) REFERENCES dm_player (player_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (team_id) REFERENCES dm_team (team_id) ON UPDATE CASCADE ON DELETE RESTRICT
);


WITH preload AS (
    SELECT sfpm.match_day_id,
        sfpm.code_fpi AS player_id,
        UPPER(SUBSTR(sfpm.team_name, 1, 3)) AS team_id,
        sfpm.goals_scored,
        sfpm.goals_conceded,
        sfpm.own_goals,
        sfpm.penalties_scored,
        sfpm.penalties_missed,
        sfpm.penalties_saved,
        sfpm.assists,
        sfpm.yellow_card,
        sfpm.red_card,
        sfpm.subbed_in,
        sfpm.subbed_out,
        sfpm.goals_scored * bonus_goal.value + sfpm.assists * bonus_assist.value + sfpm.own_goals * bonus_own_goal.value + sfpm.penalties_saved * bonus_penalty_save.value + sfpm.penalties_missed * bonus_penalty_miss.value + sfpm.yellow_card * bonus_yellow_card.value + sfpm.red_card * bonus_red_card.value + IIF(sfpm.role = 'G', sfpm.goals_conceded = 0, 0) * bonus_clean_sheet.value AS fanta_bonus_total
    FROM st_fpi_player_match AS sfpm
        CROSS JOIN dm_parameter AS bonus_goal
        CROSS JOIN dm_parameter AS bonus_assist
        CROSS JOIN dm_parameter AS bonus_clean_sheet
        CROSS JOIN dm_parameter AS bonus_penalty_save
        CROSS JOIN dm_parameter AS bonus_penalty_miss
        CROSS JOIN dm_parameter AS bonus_own_goal
        CROSS JOIN dm_parameter AS bonus_yellow_card
        CROSS JOIN dm_parameter AS bonus_red_card
    WHERE bonus_goal.key = 'bonus_goal'
        AND bonus_assist.key = 'bonus_assist'
        AND bonus_clean_sheet.key = 'bonus_clean_sheet'
        AND bonus_penalty_save.key = 'bonus_penalty_save'
        AND bonus_penalty_miss.key = 'bonus_penalty_miss'
        AND bonus_own_goal.key = 'bonus_own_goal'
        AND bonus_yellow_card.key = 'bonus_yellow_card'
        AND bonus_red_card.key = 'bonus_red_card'
)
INSERT INTO ft_player_match
SELECT preload.match_day_id,
    preload.player_id,
    preload.team_id,
    preload.goals_scored,
    preload.goals_conceded,
    preload.own_goals,
    preload.penalties_scored,
    preload.penalties_missed,
    preload.penalties_saved,
    preload.assists,
    preload.yellow_card,
    preload.red_card,
    preload.subbed_in,
    preload.subbed_out,
    preload.fanta_bonus_total
FROM preload
WHERE TRUE ON CONFLICT (match_day_id, player_id, team_id) DO
UPDATE
SET goals_scored = EXCLUDED.goals_scored,
    goals_conceded = EXCLUDED.goals_conceded,
    own_goals = EXCLUDED.own_goals,
    penalties_scored = EXCLUDED.penalties_scored,
    penalties_missed = EXCLUDED.penalties_missed,
    penalties_saved = EXCLUDED.penalties_saved,
    assists = EXCLUDED.assists,
    yellow_card = EXCLUDED.yellow_card,
    red_card = EXCLUDED.red_card,
    subbed_in = EXCLUDED.subbed_in,
    subbed_out = EXCLUDED.subbed_out,
    fanta_bonus_total = EXCLUDED.fanta_bonus_total;