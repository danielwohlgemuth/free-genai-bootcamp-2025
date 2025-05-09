CREATE TABLE IF NOT EXISTS words_groups (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    word_id INTEGER NOT NULL,
    group_id INTEGER NOT NULL,
    FOREIGN KEY (word_id) REFERENCES words (id),
    FOREIGN KEY (group_id) REFERENCES groups (id)
);