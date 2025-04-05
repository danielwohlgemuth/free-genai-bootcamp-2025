CREATE TABLE IF NOT EXISTS study_activities (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    thumbnail_url TEXT,
    description TEXT,
    type TEXT NOT NULL
);