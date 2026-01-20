CREATE TABLE IF NOT EXISTS giveaways (
    message_id INTEGER PRIMARY KEY,
    channel_id INTEGER,
    host_id INTEGER,
    prize TEXT,
    winners INTEGER,
    end_time INTEGER,
    ended INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS giveaway_entries (
    message_id INTEGER,
    user_id INTEGER,
    PRIMARY KEY (message_id, user_id)
);
