MAX_COUNT = 250


class Groups:
    def __init__(self, session, **kwargs):
        self._group_ids = kwargs['group_ids'] if 'group_ids' in kwargs else []
        self._group_ids = list(set(self._group_ids))
        self._params = kwargs
        self._session = session

    def __iter__(self):
        group_ids = []
        for i, uid in enumerate(self._group_ids):
            group_ids.append(uid)
            if i == len(self._group_ids) - 1 or len(group_ids) == MAX_COUNT:
                self._params['group_ids'] = ', '. join([str(i) for i in group_ids])
                group_ids.clear()

                response = self._session.get('groups.getById', params=self._params)
                for user in response['response']:
                    yield user

    def __len__(self):
        return len(self._group_ids)
