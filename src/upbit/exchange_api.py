import requests
import jwt
import uuid
from urllib.parse import urlencode
import hashlib
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

        if kwargs.get('data'):

            query_string = urlencode(kwargs['data']).encode()

            m = hashlib.sha512()
            m.update(query_string)
            query_hash = m.hexdigest()

            payload['query_hash'] = query_hash
            payload['query_hash_alg'] = 'SHA512'

        jwt_token = jwt.encode(payload, self.secret)
        authorize_token = 'Bearer {}'.format(jwt_token)
        headers = {"Authorization": authorize_token}

        try:
            response = method(endpoint,
                              data=kwargs.get('data', None),
                              params=kwargs.get('params', {}),
                              headers=headers,
                              timeout=600)

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

    def get_balances(self, method='', offset=0, limit=12, ticker='', filter_valid=True):

        response = self._request(requests.get, 'accounts')

        if filter_valid:
            tickers = upbit_quotation_api.get_tickers(method='set')

            if not tickers['ok']:
                return tickers

        if not response['ok']:
            return response

        if method == 'avg_buy_price':
            response['data'] = {x['unit_currency'] + '-' + x['currency']: x['avg_buy_price']
                                for x in response['data']
                                if x['currency'] != x['unit_currency']
                                and (not filter_valid or x['unit_currency'] + '-' + x['currency'] in tickers['data'])}

        elif method == 'paging':

            data = [x['unit_currency'] + '-' + x['currency']
                    for x in response['data']
                    if x['currency'] != x['unit_currency']
                    and (not filter_valid or x['unit_currency'] + '-' + x['currency'] in tickers['data'])]

            response['data'] = {
                'paginate': {
                    'total': len(data),
                    'limit': limit,
                    'offset': offset
                },
                'list': data[offset * limit: offset * limit + limit]
            }

        elif method == 'single':
            data = None
            for x in response['data']:
                if x['unit_currency'] + '-' + x['currency'] == ticker:
                    data = x
                    break

            if data == None:
                return {
                    'ok': False,
                    'description': 'You do not own this anymore'
                }

            response['data'] = data

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
            'volume': str(volume),
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

        return self.sell_market_order(ticker, price / current_price['data'][ticker])

    def buy_market_order_fee_included(self, ticker, price, fee=0.0005):

        price = price / (1 + fee)

        return self.buy_market_order(ticker, price)

    def sell_market_order_fee_included(self, ticker, price, fee=0.0005):

        price = price / (1 - fee)

        return self.sell_market_order_by_price(ticker, price)

    def sell_market_order_all(self, ticker):

        balance = self.get_balances(method='single', ticker=ticker)

        if not balance['ok']:
            return balance

        return self.sell_market_order(ticker, balance['data']['balance'])


upbit_exchange_api = UpbitExchangeApi()
