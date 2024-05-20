from serie_a_db.db.client import Db


def test_parameters_inserted_into_db_should_be_retrievable(db: Db):
    # Arrange
    parameters = {"param1": 5.0, "param2": 10.0}

    # Act
    db.meta.set_parameters(parameters)

    # Assert
    assert db.select("SELECT * FROM dm_parameter WHERE key LIKE 'param%'") == [
        ("param1", 5.0),
        ("param2", 10.0),
    ]
