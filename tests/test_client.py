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


def test_getting_table_attributes(db: Db):
    # Arrange
    db.execute("CREATE TABLE st_dummy (dummy_attr INT, dummy_attr2 STR);")

    # Act
    attributes = db.get_attributes("st_dummy")

    # Assert
    assert attributes == ("dummy_attr", "dummy_attr2")


def test_select_with_attribute_names(db: Db):
    # Arrange
    db.execute("CREATE TABLE st_dummy (dummy_attr INT, dummy_attr2 STR);")
    db.execute("INSERT INTO st_dummy VALUES (1, 'a');")

    # Act
    actual = db.select("SELECT * FROM st_dummy", include_attributes=True)

    # Assert
    assert actual == [("dummy_attr", "dummy_attr2"), (1, "a")]
