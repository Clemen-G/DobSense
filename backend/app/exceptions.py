class UserException(Exception):
    def __init__(self, http_code, user_message):
        super().__init__(self, user_message)
        self.http_code = http_code
        self.user_message = user_message