from UpbitOpenAPI import UpbitQuotationAPI
from datetime import timedelta

def string_to_ticker(string):
    ticker = string.upper()
    if len(ticker.split('-')) == 1:
        ticker = 'KRW-' + ticker
    return ticker

def get_target_price(ticker, reset_hour, get_k_value = False):
    df = UpbitQuotationAPI.get_ohlcv(ticker, "minute60", 550)

    now = df.index[-1]
    while now.hour != reset_hour:
        now = now - timedelta(hours = 1)

    lt = []

    for i in range(0,20):
        df_k = df.loc[now-timedelta(days = (1 + i)):now-timedelta(days = i, hours=1)]
        j = 1 - abs(df_k.iloc[0]["open"] - df_k.iloc[-1]["close"]) / (df_k["high"].max() - df_k["low"].min())
        lt.append(j)

    k = sum(lt) / len(lt)

    df_v = df.loc[now-timedelta(days = 1):now-timedelta(hours=1)]

    volatility = (df_v["high"].max() - df_v["low"].min())*k
    target_price = df.loc[now]["open"] + volatility
    
    if get_k_value:
        return k, target_price
    else:
        return target_price

def get_betting_ratio(ticker, current_price):
    df = UpbitQuotationAPI.get_ohlcv(ticker, "minute60", 550)
    lt = []
    for i in range(3, 21):
        ma = df.iloc[-1-(24*i):-1]["close"].mean()
        if ma <= current_price:
            lt.append(1)
        else:
            lt.append(0)
    mac = sum(lt) / len(lt)

    now = df.index[-1]

    df_v = df.loc[now-timedelta(days = 1):now-timedelta(hours=1)]

    volatility = (df_v["high"].max() - df_v["low"].min()) / current_price

    vcr = 0.02 / volatility
    if vcr > 1:
        vcr = 1

    return mac * vcr

def buy_set_price(account, ticker, betting_price, tax = 0.0005):
    price = (betting_price) / (tax + 1)
    return account.buy_market_order(ticker, price)

def sell_all(account, ticker):
    volume = account.get_balance(ticker)
    return account.sell_market_order(ticker, volume)

def sell_set_price(account, ticker, sell_price, tax = 0.0005):
    current_price = UpbitQuotationAPI.get_current_price(ticker)
    sell_volume = sell_price / (current_price * ( 1 - tax ) )
    return account.sell_market_order(ticker, sell_volume)