# serie-a-db

Building a database of results and players' grades from the Italian football league Serie A.

## DB structure

The planning of the DB can be found here: https://dbdiagram.io/d/Serie-A-db-65d201ddac844320ae66ce86

### Notes

- Serie A API for leaderboards https://www.legaseriea.it/api/stats/Classificacompleta?CAMPIONATO=A&STAGIONE=2022-23&TURNO=UNICO&GIRONE=UNI
- https://www.legaseriea.it/api/stats/live/match?extra_link&order=oldest&lang=en&season_id=157617&match_day_id=157815

Matchday 1 season 22/23
https://www.legaseriea.it/api/stats/live/match?extra_link&order=oldest&lang=en&season_id=150052&page=1&limit=20&pag&match_day_id=150194

Matchday 1 season 21/22
https://www.legaseriea.it/api/stats/live/match?extra_link&order=oldest&lang=en&season_id=30030&page=1&limit=20&pag&match_day_id=30093

https://www.legaseriea.it/api/stats/live/match?extra_link&order=oldest&lang=en&season_id=150051&page=1&limit=20&pag&match_day_id=150193

All matchdays of a season
https://www.legaseriea.it/api/season/120076/championship/A/matchday?lang=it
