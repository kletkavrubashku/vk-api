def users(session, **kwargs):
    if 'user_ids' in kwargs:
        kwargs['user_ids'] = ', '. join([str(i) for i in kwargs['user_ids']])
    response = session.get('users.get', params=kwargs)
    return response['response']
