class Messages:
    def __init__(self, session, **kwargs):
        params = {'count': 200}
        params.update(kwargs)
        response = session.get('messages.get', params=params)
        self._data = response['response'][1:]

    def __iter__(self):
        return iter(self._data)


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

    process_item(item, _process_attachment, fwd_messages=fwd_messages)
