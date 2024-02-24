CREATE TABLE IF NOT EXISTS ft_tables_update (
    table_name STR PRIMARY KEY,
    datetime_update STR PRIMARY KEY CHECK date_updated IS datetime(date_updated),
    number_of_rows INT NOT NULL
);