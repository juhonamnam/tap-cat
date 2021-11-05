from datetime import timedelta
import pandas as pd
from UpbitOpenAPI import UpbitQuotationAPI

def get_target_prices(ticker, hour, days):
    df = UpbitQuotationAPI.get_ohlcv(ticker, "minute60", 24 * days + 550)
    k_lt = []
    target_price_lt = []
    high_lt = []
    close_lt = []

    now = df.index[-1]
    while now.hour != hour:
        now = now - timedelta(hours = 1)

    for d in range(days):

        lt = []

        for i in range(0,20):
            df_k = df.loc[now-timedelta(days = (1 + i)):now-timedelta(days = i, hours=1)]
            j = 1 - abs(df_k.iloc[0]["open"] - df_k.iloc[-1]["close"]) / (df_k["high"].max() - df_k["low"].min())
            lt.append(j)

        k = sum(lt) / len(lt)
        k_lt.append(k)

        df_v = df.loc[now-timedelta(days = 1):now-timedelta(hours=1)]

        volatility = (df_v["high"].max() - df_v["low"].min())*k

        target_price = df.loc[now]["open"] + volatility
        target_price_lt.append(target_price)

        high_lt.append(df_v["high"].max())
        close_lt.append(df_v.iloc[-1]["close"])

        now = now - timedelta(days = 1)

    k_lt.reverse()
    target_price_lt.reverse()
    high_lt.reverse()
    close_lt.reverse()

    return [k_lt, target_price_lt, high_lt, close_lt]


def backtest():

    ticker = input("Ticker:")
    reset_hour = int(input("Reset Hour:"))
    days = int(input("Days:"))

    k_lt, target_price_lt, high_lt, close_lt = get_target_prices(ticker, reset_hour, days+1)
    df = pd.DataFrame()
    df["high"] = high_lt
    df["close"] = close_lt
    df["target price"] = target_price_lt
    df["target price"] = df["target price"].shift(1)
    df["buy condition"] = (df["high"] >= df["target price"])
    df["interest"] = (df["close"] * 0.9995) / (df["target price"] * 1.0005)
    df["interest"] = df["interest"][df["buy condition"]]
    df["interest"].cumprod().iloc[-1]
    df["interest"].prod()

    print(df["interest"].prod())

    return df, df["interest"].prod()


if __name__ == "__main__":
    backtest()