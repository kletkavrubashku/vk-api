class Messages:
    def __init__(self, session, **kwargs):
        params = {'count': 200}
        params.update(kwargs)
        self._response = session.get('messages.get', params=params)['response']
        self._data = self._response[1:]

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return self._response[0]


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
