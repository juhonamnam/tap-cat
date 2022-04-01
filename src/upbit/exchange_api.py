import requests
import jwt
import uuid
import logging
from .quotation_api import upbit_quotation_api


class UpbitExchangeApi:
    def __init__(self):
        self.logger = logging.getLogger('upbit_exchange_api')

    def config(self, access, secret):
        self.access = access
        self.secret = secret

    def _request(self, method, endpoint, **kwargs):
        if not self.access or not self.secret:
            return {
                'ok': False,
                'description': 'Access key and secret key is missing'
            }

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

    def buy_market_order(self, ticker, price):

        data = {
            'market': ticker,
            'side': 'bid',
            'price': str(price),
            'ord_type': 'price'
        }

        response = self._request(requests.post, 'orders', data=data)

        if response['ok']:
            self.logger.info(
                f'Buy: Result: {str(response)} Data: {data}')
        else:
            self.logger.error(
                f'Buy: Result: {str(response)} Data: {data}')

        return response

    def sell_market_order(self, ticker, volume):

        data = {
            'market': ticker,
            'side': 'ask',
            'price': str(volume),
            'ord_type': 'market'
        }

        response = self._request(requests.post, 'orders', data=data)

        if response['ok']:
            self.logger.info(
                f'Sell: Result: {str(response)} Data: {data}')
        else:
            self.logger.error(
                f'Sell: Result: {str(response)} Data: {data}')

        return response

    def sell_market_order_by_price(self, ticker, price):

        current_price = upbit_quotation_api.get_current_prices(ticker)

        if not current_price['ok']:
            return current_price

        price / current_price['data'][ticker]

    def buy_market_order_fee_included(self, ticker, price, fee=0.0005):

        price = price / (1 + fee)

        return self.buy_market_order(ticker, price)

    def sell_market_order_fee_included(self, ticker, price, fee=0.0005):

        price = price / (1 - fee)

        return self.sell_market_order_by_price(ticker, price)


upbit_exchange_api = UpbitExchangeApi()
