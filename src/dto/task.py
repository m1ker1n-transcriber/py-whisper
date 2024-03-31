class TaskDTO:
    def __init__(self, telegram_user_id: str, telegram_msg_id: str, voice_id: str):
        self.telegram_user_id = telegram_user_id
        self.telegram_msg_id = telegram_msg_id
        self.voice_id = voice_id

