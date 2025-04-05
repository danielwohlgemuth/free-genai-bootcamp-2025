CREATE TABLE IF NOT EXISTS study_activities (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    name TEXT NOT NULL,
    thumbnail_url TEXT,
    description TEXT,
    type TEXT NOT NULL
);