CREATE TABLE IF NOT EXISTS ft_tables_update (
    table_name STR PRIMARY KEY,
    date_updated STR NOT NULL CHECK date_updated IS date(date_updated)
);