MAX_COUNT = 200


class Messages:
    def __init__(self, session, **kwargs):
        if 'count' in kwargs:
            self._limit = kwargs['count']
            kwargs['count'] = min(kwargs['count'], MAX_COUNT)
        else:
            kwargs['count'] = MAX_COUNT

        if 'offset' in kwargs:
            self._offset = kwargs['offset']
        else:
            kwargs['offset'] = 0

        self._params = kwargs
        self._session = session

        self._response = self._session.get('messages.get', params=self._params)['response']
        self._data = self._response[1:]

    def __iter__(self):
        while True:
            for i in self._data:
                yield i

            self._params['offset'] += self._params['count']
            if hasattr(self, '_limit'):
                self._params['count'] = min(self._limit - self._params['offset'], MAX_COUNT)
                if self._params['count'] == 0:
                    break
            else:
                self._params['count'] = MAX_COUNT

            self._response = self._session.get('messages.get', params=self._params)['response']
            self._data = self._response[1:]

            if not self._data:
                break

    def __len__(self):
        init_offset = self._offset if hasattr(self, '_offset') else 0
        init_count = self._limit if hasattr(self, '_limit') else self._response[0]
        return init_count - init_offset


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
