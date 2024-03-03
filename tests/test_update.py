from serie_a_db.update.update import DbTable


def test_table_name():
    class DmSeason(DbTable):
        pass

    assert DmSeason.table_name() == "dm_season"

    class DmMatchDay(DbTable):
        pass

    assert DmMatchDay.table_name() == "dm_match_day"
