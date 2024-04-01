from datetime import datetime

import pytest

from serie_a_db import utils
from serie_a_db.db.build import create_meta_tables
from serie_a_db.db.db import Db


@pytest.fixture(name="db")
def in_memory_db():
    """Provide a Db instance in memory."""
    db = Db.in_memory()
    create_meta_tables(db)
    try:
        yield db
    finally:
        db.close_connection()


@pytest.fixture()
def freeze_time():
    """Freeze time to 2024-01-01 12:00:00."""
    utils.FREEZE_TIME_TO = datetime(2024, 1, 1, 12, 0, 0)
    yield
    utils.FREEZE_TIME_TO = None
