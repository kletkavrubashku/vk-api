from oauthlib.oauth2.rfc6749.clients import WebApplicationClient
from requests_oauthlib import OAuth2Session
from configparser import ConfigParser

_AUTH_URL = 'https://oauth.vk.com/authorize'
_TOKEN_URL = 'https://oauth.vk.com/access_token'
_METHOD_URL = 'https://api.vk.com/method'
_ACCESS_TOKEN_CACHE_FN = 'access_token.cache'


def _read_cached_access_token():
    config = ConfigParser()
    config.read(_ACCESS_TOKEN_CACHE_FN)
    return config.get('session', 'access_token') if config.has_section('session') else None


def _write_cached_access_token(value):
    config = ConfigParser()
    config.add_section('session')
    config.set('session', 'access_token', value)
    config_file = open(_ACCESS_TOKEN_CACHE_FN, 'w')
    config.write(config_file)
    config_file.close()


class SessionException(Exception):
    def __init__(self, code, msg):
        self.code = code
        self.msg = msg

    def __str__(self):
        return 'Code: {}. Message: {}'.format(self.code, self.msg)


class Session:
    def __init__(self, app_id, app_secret_key, scope):
        client = WebApplicationClient(app_id, default_token_placement = 'query')
        self._session = OAuth2Session(scope=scope, client=client)
        self._authorization_url, _ = self._session.authorization_url(_AUTH_URL)
        self._secret_key = app_secret_key

        access_token_cache_tmp = _read_cached_access_token()
        if access_token_cache_tmp:
            self._session.token = {'access_token': access_token_cache_tmp}

    def _ensure_access_token(self):
        print('Пройдите по указанному адресу и авторизуйтесь:\n{}'.format(self._authorization_url))

        auth_resp = input('Введите адрес, на который вы были перенаправлены после прохождения авторизации:\n')
        auth_resp = auth_resp.replace('#', '?').strip()

        token = self._session.fetch_token(_TOKEN_URL, client_secret=self._secret_key, authorization_response=auth_resp)
        _write_cached_access_token(token['access_token'])

    def get(self, method, **kwargs):
        url = '/'.join([_METHOD_URL, method])
        response = self._session.get(url, **kwargs).json()
        if 'error' in response:
            error = response['error']
            code = error['error_code']
            if code is 5:
                self._ensure_access_token()
                return self.get(method, **kwargs)
            raise SessionException(code, error['error_msg'])
        else:
            return response
