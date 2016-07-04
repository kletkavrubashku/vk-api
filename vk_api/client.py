from .messages import Messages
from .session import Session


class Client:
    def __init__(self, app_id, app_secret_key, scope):
        self._session = Session(app_id, app_secret_key, scope)

    def get_messages(self):
        return Messages(self._session)
