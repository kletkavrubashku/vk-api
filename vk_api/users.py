MAX_COUNT = 250


class Users:
    def __init__(self, session, **kwargs):
        self._user_ids = kwargs['user_ids'] if 'user_ids' in kwargs else []
        self._user_ids = list(set(self._user_ids))
        self._params = kwargs
        self._session = session

    def __iter__(self):
        user_ids = []
        for i, uid in enumerate(self._user_ids):
            user_ids.append(uid)
            if i == len(self._user_ids) - 1 or len(user_ids) == MAX_COUNT:
                self._params['user_ids'] = ', '. join([str(i) for i in user_ids])
                user_ids.clear()

                response = self._session.get('users.get', params=self._params)
                for user in response['response']:
                    yield user

    def __len__(self):
        return len(self._user_ids)
