class Messages:
    def __init__(self, session):
        response = session.get('messages.get', params={'count':'200'})
        self._data = response['response'][1:]

    def __iter__(self):
        return iter(self._data)
