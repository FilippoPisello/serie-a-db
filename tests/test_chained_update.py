from unittest.mock import Mock

from serie_a_db.db.build import update_db


def test_one_layer_of_dependency(db):
    depended_upon_table = _mock_table()

    dependant_table = _mock_table()
    dependant_table.DEPENDS_ON = (depended_upon_table,)

    update_db(db, tables=(dependant_table,))

    depended_upon_table.update.assert_called_once()
    dependant_table.update.assert_called_once()


def test_two_layers_of_dependency(db):
    depended_upon_table = _mock_table()

    dependant_table = _mock_table()
    dependant_table.DEPENDS_ON = (depended_upon_table,)

    dependant_dependant_table = _mock_table()
    dependant_dependant_table.DEPENDS_ON = (dependant_table,)

    update_db(db, tables=(dependant_dependant_table,))

    depended_upon_table.update.assert_called_once()
    dependant_table.update.assert_called_once()
    dependant_dependant_table.update.assert_called_once()


def _mock_table(depends_on: tuple = ()) -> Mock:
    table = Mock()
    table.DEPENDS_ON = depends_on
    table.from_definitions.return_value = table
    return table
