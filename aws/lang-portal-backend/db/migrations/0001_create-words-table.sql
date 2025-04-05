CREATE TABLE IF NOT EXISTS words (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    japanese TEXT NOT NULL,
    romaji TEXT NOT NULL,
    english TEXT NOT NULL,
    parts JSONB
);