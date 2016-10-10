def decorator(func):
    def _freeze(obj):
        if isinstance(obj, dict):
            return frozenset({k: _freeze(v) for k, v in obj.items()}.items())

        if isinstance(obj, list):
            return tuple([_freeze(v) for v in obj])

        return obj

    def wrapper(*args, caching=False, **kwargs):
        if caching:
            args_hash = _freeze(args)
            kwargs_hash = _freeze(kwargs)

            if hasattr(wrapper, 'cache') and args_hash in wrapper.cache and kwargs_hash in wrapper.cache[args_hash]:
                return wrapper.cache[args_hash][kwargs_hash]

            result = func(*args, **kwargs)

            wrapper.cache = {}
            wrapper.cache.update({args_hash: {kwargs_hash: result}})

            return result
        return func(*args, **kwargs)
    return wrapper
