from collections import namedtuple

import pytest

from serie_a_db.update.update import DbTable


def test_table_name():
    class DmSeason(DbTable):
        pass

    assert DmSeason.table_name() == "dm_season"

    class DmMatchDay(DbTable):
        pass

    assert DmMatchDay.table_name() == "dm_match_day"


class TestDataCompatibilityCheck:

    def test_error_if_data_incompatible(self):
        season = namedtuple("Season", ["season_id", "season_name"])
        data = [season(2021, "2021/22")]
        # The columns are in the wrong order
        columns = ["season_name", "season_id"]
        with pytest.raises(ValueError):
            DbTable.error_if_data_incompatible(data, columns)

    def test_no_error_if_data_compatible(self):
        season = namedtuple("Season", ["season_id", "season_name"])
        data = [season(2021, "2021/22")]
        columns = ["season_id", "season_name"]
        DbTable.error_if_data_incompatible(data, columns)
