CREATE TABLE IF NOT EXISTS words (
    id SERIAL PRIMARY KEY,
    japanese TEXT NOT NULL,
    romaji TEXT NOT NULL,
    english TEXT NOT NULL,
    parts JSONB
);