from oauthlib.oauth2.rfc6749.clients import WebApplicationClient
from requests_oauthlib import OAuth2Session

_AUTH_URL = 'https://oauth.vk.com/authorize'
_TOKEN_URL = 'https://oauth.vk.com/access_token'
_METHOD_URL = 'https://api.vk.com/method'


class Session:
    def __init__(self, app_id, app_secret_key, scope):
        client = WebApplicationClient(app_id, default_token_placement = 'query')
        self._session = OAuth2Session(scope=scope, client=client)
        self._authorization_url, _ = self._session.authorization_url(_AUTH_URL)
        self._secret_key = app_secret_key
        self._authorize()

    def _authorize(self):
        print('Пройдите по указанному адресу и авторизуйтесь:\n', self._authorization_url)

        auth_resp = input('Введите адрес, на который вы были перенаправлены после прохождения авторизации:\n')
        auth_resp = auth_resp.replace('#', '?').strip()

        self._session.fetch_token(_TOKEN_URL, client_secret=self._secret_key, authorization_response=auth_resp)

    def get(self, method, **kwargs):
        url = '/'.join([_METHOD_URL, method])
        return self._session.get(url, **kwargs)