CREATE TABLE IF NOT EXISTS application_stats (
    user_id INTEGER,
    application_type TEXT,
    submitted_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS application_blacklist (
    user_id INTEGER PRIMARY KEY,
    reason TEXT

);
CREATE TABLE IF NOT EXISTS application_cooldowns (
    user_id INTEGER NOT NULL,
    application_type TEXT NOT NULL,
    last_applied INTEGER NOT NULL,
    PRIMARY KEY (user_id, application_type)
);
