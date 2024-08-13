CREATE TABLE IF NOT EXISTS dm_data_source (
    data_source_id STR PRIMARY KEY,
    name STR NOT NULL
);


INSERT INTO dm_data_source (data_source_id, name)
VALUES ('FM', 'Fantamaster'),
    ('FPI', 'FantaCalcio.it') ON CONFLICT DO
UPDATE
SET name = EXCLUDED.name;