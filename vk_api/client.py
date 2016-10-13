from .groups import Groups
from .messages import Messages
from .session import Session
from .users import Users


class Client:
    def __init__(self, app_id, app_secret_key, scope):
        self._session = Session(app_id, app_secret_key, scope)

    def get_messages(self, **kwargs):
        return Messages(self._session, **kwargs)

    def get_users(self, **kwargs):
        return Users(self._session, **kwargs)

    def get_groups(self, **kwargs):
        return Groups(self._session, **kwargs)
