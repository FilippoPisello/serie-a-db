WITH stats AS (
    SELECT fpm.player_id,
        SUM(1) AS appearances,
        SUM(fpm.goals_scored) AS goals_scored,
        SUM(fpm.assists) AS assists,
        SUM(fpm.goals_conceded) AS goals_conceded,
        SUM(fpm.penalties_scored) AS penalties_scored,
        SUM(fpm.penalties_missed) AS penalties_missed,
        SUM(fpm.yellow_card) AS yellow_cards,
        SUM(fpm.red_card) AS red_cards,
        SUM(fpm.red_card) * 2 + SUM(fpm.yellow_card) AS converted_cards,
        ROUND(AVG(fpg.grade), 2) AS grade,
        ROUND(AVG(fpg.grade + fpm.fanta_bonus_total), 2) AS fanta_grade,
        SUM(
            IIF(
                dmd.number BETWEEN 1 AND 19,
                1,
                NULL
            )
        ) AS first_half_appearances,
        ROUND(
            AVG(
                IIF(
                    dmd.number BETWEEN 1 AND 19,
                    fpg.grade + fpm.fanta_bonus_total,
                    NULL
                )
            ),
            2
        ) AS first_half_fanta_grade,
        SUM(
            IIF(
                dmd.number BETWEEN 20 AND 38,
                1,
                NULL
            )
        ) AS second_half_appearances,
        ROUND(
            AVG(
                IIF(
                    dmd.number BETWEEN 20 AND 38,
                    fpg.grade + fpm.fanta_bonus_total,
                    NULL
                )
            ),
            2
        ) AS second_half_fanta_grade
    FROM ft_player_match AS fpm
        INNER JOIN dm_match_day AS dmd ON fpm.match_day_id = dmd.match_day_id
        INNER JOIN dm_season AS dms ON dmd.season_id = dms.season_id
        AND dms.year_start = 2023
        INNER JOIN ft_player_grade AS fpg ON fpm.player_id = fpg.player_id
        AND fpm.team_id = fpg.team_id
        AND fpm.match_day_id = fpg.match_day_id
        AND fpg.data_source_id = 'FPI'
    GROUP BY fpm.player_id
)
SELECT sfmp.name,
    sfmp.role,
    sfmp.team_id,
    sfmp.value,
    s.*
FROM st_fm_player AS sfmp
    LEFT JOIN st_player_cross_source_mapping AS spcsm ON sfmp.code_fm = spcsm.code_fm
    LEFT JOIN stats AS s ON spcsm.code_fpi = s.player_id
WHERE sfmp.load_ts = (
        SELECT MAX(load_ts)
        FROM st_fm_player
    )
ORDER BY sfmp.team_id,
    sfmp.role,
    sfmp.value DESC;