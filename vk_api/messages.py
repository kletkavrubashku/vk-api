class Messages:
    def __init__(self, session, **kwargs):
        if 'count' in kwargs:
            self._manual = True
        else:
            self._manual = False
            kwargs['count'] = 200
        kwargs['offset'] = kwargs['offset'] if 'offset' in kwargs else 0

        self._params = kwargs
        self._session = session

        self._response = self._session.get('messages.get', params=self._params)['response']
        self._data = self._response[1:]

    def __iter__(self):
        offset = self._params['offset'] + self._params['count']
        while True:
            for i in self._data:
                yield i

            if self._manual:
                break

            params = {'offset': offset}
            params.update(self._params)
            self._response = self._session.get('messages.get', params=params)['response']
            self._data = self._response[1:]

            if not self._data:
                break

            offset += self._params['count']

    def __len__(self):
        if self._manual:
            return self._params['count']
        return self._response[0] - self._params['offset']


def process_item(item, callback, *, fwd_messages=False):
    callback(item)
    if fwd_messages and 'fwd_messages' in item:
        for fwd_item in item['fwd_messages']:
            process_item(fwd_item, callback, fwd_messages=fwd_messages)


def process_attachments(item, callback, *, fwd_messages=False):
    def _process_attachment(item):
        if 'attachments' in item:
            for att_item in item['attachments']:
                callback(att_item)
                _process_attachment(att_item[att_item['type']])

    process_item(item, _process_attachment, fwd_messages=fwd_messages)
