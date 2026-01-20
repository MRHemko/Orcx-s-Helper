class ApplicationSession:
    def __init__(self, user_id: int, app_key: str):
        self.user_id = user_id
        self.app_key = app_key
        self.answers = {}
        self.index = 0

SESSIONS: dict[int, ApplicationSession] = {}
