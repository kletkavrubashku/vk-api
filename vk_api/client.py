from .groups import groups
from .messages import Messages
from .session import Session
from .users import users
import caching


class Client:
    def __init__(self, app_id, app_secret_key, scope):
        self._session = Session(app_id, app_secret_key, scope)

    @caching.decorator
    def get_messages(self, **kwargs):
        return Messages(self._session, **kwargs)

    @caching.decorator
    def get_users(self, **kwargs):
        return users(self._session, **kwargs)

    @caching.decorator
    def get_groups(self, **kwargs):
        return groups(self._session, **kwargs)
