CREATE TABLE IF NOT EXISTS ft_tables_update (
    table_name STR,
    datetime_updated STR CHECK (
        datetime_updated = strftime('%Y-%m-%d %H:%M:%f', datetime_updated)
    ),
    rows_number INT NOT NULL,
    PRIMARY KEY (table_name, datetime_updated)
);