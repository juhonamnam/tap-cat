import requests
import jwt
import uuid
import hashlib
from urllib.parse import urlencode
from UpbitOpenAPI import UpbitQuotationAPI

class Account:
    def __init__(self, access, secret):
        self.access = access
        self.secret = secret

    def get_balances(self):

        url = "https://api.upbit.com/v1/accounts"

        payload = {
            'access_key': self.access,
            'nonce': str(uuid.uuid4()),
        }

        jwt_token = jwt.encode(payload, self.secret)
        authorize_token = 'Bearer {}'.format(jwt_token)
        headers = {"Authorization": authorize_token}

        res = requests.get(url, headers=headers)

        return res.json()

    def get_balance(self, ticker = "KRW"):

        try:
            
            balances = self.get_balances()
            
            balance = 0
            
            if "-" in ticker:
                ticker = ticker.split("-")[1]
                
            for x in balances:
                if x["currency"] == ticker:
                    balance = float(x["balance"])
                    break
            
            return balance

        except Exception as x:
            # print(x.__class__.__name__)
            return None

    def get_estimated_balance(self):
        balances = self.get_balances()

        balance = 0
        dt = dict()
        for b in balances:
            if b['currency'] == 'KRW':
                balance += float(b['balance'])
            else:
                ticker = 'KRW-' + b['currency']
                dt[ticker] = float(b['balance'])

        current_prices = UpbitQuotationAPI.get_current_prices([dt.keys()])

        for i, j in dt.items():
            balance += j * current_prices[i]
            
        return balance

    def buy_market_order(self, ticker, price):
        
        try:
            
            url = "https://api.upbit.com/v1/orders"
            
            query = {
    	        'market': ticker,
        	    'side': 'bid',
            	'price': str(price),
	            'ord_type': 'price',
    	    }
            
            query_string = urlencode(query).encode()
            
            m = hashlib.sha512()
            m.update(query_string)
            query_hash = m.hexdigest()
            
            payload = {
    	        'access_key': self.access,
	            'nonce': str(uuid.uuid4()),
    	        'query_hash': query_hash,
       	    	'query_hash_alg': 'SHA512',
	        }
            
            jwt_token = jwt.encode(payload, self.secret)
            authorize_token = 'Bearer {}'.format(jwt_token)
            headers = {"Authorization": authorize_token}
            
            res = requests.post(url, params=query, headers=headers)
            return res.json()

        except Exception as x:
            print(x.__class__.__name__)
            return None

    def sell_market_order(self, ticker, volume):
        
        try:
            url = "https://api.upbit.com/v1/orders"
            
            query = {
                'market': ticker,
                'side': 'ask',
                'volume': str(volume),
                'ord_type': 'market',
	        }
            
            query_string = urlencode(query).encode()
            
            m = hashlib.sha512()
            m.update(query_string)
            query_hash = m.hexdigest()
            
            payload = {
                'access_key': self.access,
                'nonce': str(uuid.uuid4()),
                'query_hash': query_hash,
                'query_hash_alg': 'SHA512',
	        }
            
            jwt_token = jwt.encode(payload, self.secret)
            authorize_token = 'Bearer {}'.format(jwt_token)
            headers = {"Authorization": authorize_token}
            
            res = requests.post(url, params=query, headers=headers)
            return res.json()

        except Exception as x:
            print(x.__class__.__name__)
            return None

    def get_order(self, uuids):
        
        url = 'https://api.upbit.com/v1/orders'

        query = {
            'state': 'done',
        }
        query_string = urlencode(query)

        uuids_query_string = '&'.join(["uuids[]={}".format(uuid) for uuid in uuids])

        query['uuids[]'] = uuids
        query_string = "{0}&{1}".format(query_string, uuids_query_string).encode()

        m = hashlib.sha512()
        m.update(query_string)
        query_hash = m.hexdigest()

        payload = {
            'access_key': self.access,
            'nonce': str(uuid.uuid4()),
            'query_hash': query_hash,
            'query_hash_alg': 'SHA512',
        }

        jwt_token = jwt.encode(payload, self.secret)
        authorize_token = 'Bearer {}'.format(jwt_token)
        headers = {"Authorization": authorize_token}

        res = requests.get(url, params=query, headers=headers)

        return res.json()