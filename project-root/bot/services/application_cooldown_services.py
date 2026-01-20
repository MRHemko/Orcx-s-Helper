from datetime import datetime, timedelta
from bot.database.connections import db

COOLDOWN_DAYS = 14

def can_apply(user_id: int) -> bool:
    row = db.fetchone(
        "SELECT last_applied FROM application_cooldowns WHERE user_id = ?",
        (user_id,)
    )
    if not row:
        return True

    return datetime.utcnow() - row[0] > timedelta(days=COOLDOWN_DAYS)

def save_application(user_id: int):
    db.execute(
        "INSERT OR REPLACE INTO application_cooldowns VALUES (?, ?)",
        (user_id, datetime.utcnow())
    )
