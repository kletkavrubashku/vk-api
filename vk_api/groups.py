def groups(session, **kwargs):
    if 'group_ids' in kwargs:
        kwargs['group_ids'] = ', '. join([str(i) for i in kwargs['group_ids']])
    response = session.get('groups.getById', params=kwargs)
    return response['response']
