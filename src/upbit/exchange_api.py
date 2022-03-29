import requests
import jwt
import uuid


class UpbitExchangeApi:
    def __init__(self, access, secret):
        self.access = access
        self.secret = secret

    def _request(self, method, endpoint, **kwargs):
        base_api = "https://api.upbit.com/v1/{endpoint}"
        endpoint = base_api.format(endpoint=endpoint)

        payload = {
            'access_key': self.access,
            'nonce': str(uuid.uuid4()),
        }
        jwt_token = jwt.encode(payload, self.secret)
        authorize_token = 'Bearer {}'.format(jwt_token)
        headers = {"Authorization": authorize_token}

        try:
            response = method(endpoint,
                              data=kwargs.get('data', None),
                              params=kwargs.get('params', {}),
                              headers=headers)

            data = response.json()

            if type(data) == dict and data.get('error'):
                return {
                    'ok': False,
                    'description': data.get('error', {}).get('message', 'Unknown Error')
                }

            return {
                'ok': True,
                'data': data
            }

        except requests.exceptions.ConnectionError:
            return {
                'ok': False,
                'description': 'Connection Error'
            }
        except Exception as e:
            return {
                'ok': False,
                'description': str(e),
            }

    def get_balances(self):

        response = self._request(requests.get, 'accounts')

        return response
