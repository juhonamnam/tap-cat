import requests
import pandas as pd
import datetime 
import time

def get_tickers(fiat = '', ticker_only = True):

    try:
        url = "https://api.upbit.com/v1/market/all?isDetails=false"

        querystring = {}

        headers = {"Accept": "application/json"}

        response = requests.request("GET", url, headers=headers, params = querystring)

        if ticker_only:    
            return [x['market'] for x in response.json() if x['market'].startswith(fiat)]
        
        else:
            return response.json()

    except Exception as x:
        print(x.__class__.__name__)
        return None

def get_current_prices(ticker = "KRW-BTC"):
    
    try:
        url = "https://api.upbit.com/v1/ticker"

        querystring = {"markets" : ticker}

        headers = {"Accept": "application/json"}

        response = requests.request("GET", url, headers=headers, params = querystring)

        price = {x['market']: x['trade_price'] for x in response.json()}

        return price

    except Exception as x:
        print(x.__class__.__name__)
        return None

def get_current_price(ticker = "KRW-BTC"):
    
    try:
        url = "https://api.upbit.com/v1/ticker"

        querystring = {"markets" : ticker}

        headers = {"Accept": "application/json"}

        response = requests.request("GET", url, headers=headers, params = querystring)

        price = response.json()[0]['trade_price']

        return price

    except Exception as x:
        print(x.__class__.__name__)

def get_url_ohlcv(interval):
    if interval in ["day", "days"]:
        url = "https://api.upbit.com/v1/candles/days"
    elif interval in ["minute1", "minutes1"]:
        url = "https://api.upbit.com/v1/candles/minutes/1"
    elif interval in ["minute3", "minutes3"]:
        url = "https://api.upbit.com/v1/candles/minutes/3"
    elif interval in ["minute5", "minutes5"]:
        url = "https://api.upbit.com/v1/candles/minutes/5"
    elif interval in ["minute10", "minutes10"]:
        url = "https://api.upbit.com/v1/candles/minutes/10"
    elif interval in ["minute15", "minutes15"]:
        url = "https://api.upbit.com/v1/candles/minutes/15"
    elif interval in ["minute30", "minutes30"]:
        url = "https://api.upbit.com/v1/candles/minutes/30"
    elif interval in ["minute60", "minutes60"]:
        url = "https://api.upbit.com/v1/candles/minutes/60"
    elif interval in ["minute240", "minutes240"]:
        url = "https://api.upbit.com/v1/candles/minutes/240"
    elif interval in ["week",  "weeks"]:
        url = "https://api.upbit.com/v1/candles/weeks"
    elif interval in ["month", "months"]:
        url = "https://api.upbit.com/v1/candles/months"
    else:
        url = "https://api.upbit.com/v1/candles/days"

    return url

def get_ohlcv(ticker = "KRW-BTC", interval = "day", count =200):

    try:
        to = datetime.datetime.now()

        dfs = []

        for pos in range(count, 0, -200):

            if to.tzinfo is None:
                to = to.astimezone()
            to = to.astimezone(datetime.timezone.utc)
            to = to.strftime("%Y-%m-%d %H:%M:%S")

            url = get_url_ohlcv(interval)

            querystring = {"market":ticker, "count":count, "to" : to}

            headers = {"Accept": "application/json"}

            response = requests.request("GET", url, headers=headers, params=querystring)

            data = response.json()

            data_index = [datetime.datetime.strptime(x['candle_date_time_kst'], "%Y-%m-%dT%H:%M:%S") for x in data]

            df = pd.DataFrame(data, columns = [
                "opening_price",
                "high_price",
                "low_price",
                "trade_price",
                "candle_acc_trade_volume",
                "candle_acc_trade_price"],
                index = data_index)

            df = df.sort_index()

            if df.shape[0] == 0:
                break
            dfs += [df]

            to = df.index[0].to_pydatetime()

            if pos > 200:
                time.sleep(0.1)

        df = pd.concat(dfs).sort_index()

        df = df.rename(columns={"opening_price": "open", 
            "high_price": "high", 
            "low_price": "low", 
            "trade_price": "close",
            "candle_acc_trade_volume": "volume", 
            "candle_acc_trade_price": "value"})

        return df

    except Exception as x:
        print(x.__class__.__name__)
        return None

