# =========================
# GENERAL
# =========================
GUILD_ID = 1378407104632586373

# =========================
# ROLES
# =========================

APPLICATION_ROLES = {
    "staff": 111111111111111111,
    "chat_mod": 222222222222222222,
    "partner_manager": 333333333333333333
}

STAFF_ROLE_ID = 1444614803518914752
CHATMOD_ROLE_ID = 1459972986873450697
PARTNER_MANAGER_ROLE_ID = 1447944654858223757
# =========================
# APPLICATIONS
# =========================
APPLICATION_REVIEW_CHANNEL_ID = 1444614714637156486
APPLICATION_COOLDOWN_HOURS = 24

APPLICATION_ROLES = {
    "staff": STAFF_ROLE_ID,
    "chatmod": CHATMOD_ROLE_ID,
    "partner_manager": PARTNER_MANAGER_ROLE_ID
}

APPLICATIONS = {
    "staff": {
        "title": "🛡 Staff Application",
        "log_channel_id": 1234567890,
        "role_on_accept": 1111111111,
        "questions": [
            {
                "id": "age",
                "type": "text",
                "question": "How old are you?"
            },
            {
                "id": "experience",
                "type": "choice",
                "question": "Do you have previous staff experience?",
                "options": ["Yes", "No"]
            },
            {
                "id": "timezone",
                "type": "text",
                "question": "What is your timezone?"
            }
        ]
    },

    "chatmod": {
        "title": "💬 Chat Moderator Application",
        "log_channel_id": 1234567890,
        "role_on_accept": 2222222222,
        "questions": [
            {
                "id": "activity",
                "type": "choice",
                "question": "How active are you?",
                "options": ["1-2h/day", "3-5h/day", "5h+/day"]
            }
        ]
    }
}

# =========================
# TICKETS
# =========================
TICKET_CATEGORY_ID = 1399019150529134602
TRANSCRIPT_LOG_CHANNEL_ID = 1444618133448032388

SUPPORT_ROLE_ID = 1456322413259133173
PARTNER_ROLE_ID = 1456322513637212373

# =========================
# GIVEAWAY
# =========================
DAILY_GIVEAWAY_CHANNEL_ID = 1400833986934210634
GIVEAWAY_PING_ROLE_ID = 1403064172627103846

ALLOWED_GIVEAWAY_CHANNEL_IDS = [
    1378407284090077204,
    1400833986934210634,
    1441413547082121379
]

MUTE_ROLE_ID = 1452633828811341874
MOD_LOG_CHANNEL_ID = 1463214235357020261

LOCK_EMOJI = "🔒"
UNLOCK_EMOJI = "🔓"