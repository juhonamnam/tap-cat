import threading
from TradeMethod.volatility import *
from datetime import timedelta, datetime
import time

# A class that sets buy margin
class BuyMargin:

    def __init__(self, ticker, reset_hour):

    # Set the target price at the start
        self.ticker = ticker
        self.target_price = get_target_price(ticker, reset_hour)
        self.bought = False

    def should_i_buy(self, price):
        
    # Return True if you should buy, False the otherwise
        if price >= self.target_price:
            self.bought = True
            return True
        else:
            return False

    def set_new_target(self, reset_hour):
    # Reset the target price

        self.target_price = get_target_price(self.ticker, reset_hour)
        self.bought = False
    

# A thread that runs auto-trade algorithm
class VBSThread(threading.Thread):

    def __init__(self, account, tickers, betting, message, record, reset_hour = None):
        threading.Thread.__init__(self)
        self.daemon = True

        # Initial variables
        self.account = account
        self.tickers = tickers
        self.betting = betting
        self.message = message
        self.record = record
        self.reset_hour = reset_hour
        self.hold_tr = False
        self.working = False

    def run(self):

        self.working = True

        # Set reset hour
        if self.reset_hour == None:
            self.reset_hour = datetime.now().hour

        # Initialize BuyMargin classes
        self.buy_margins = []
        for ticker in self.tickers:
            self.buy_margins.append(BuyMargin(ticker = ticker, reset_hour = self.reset_hour))
            time.sleep(1)

        # Indicate the starting balance
        current_time = datetime.now()
        current_time = current_time.strftime("%Y/%m/%d %H:%M")
        current_balance = self.account.get_balance()
        est_balance = self.account.get_estimated_balance()
        msg = f"--[{current_time}]-- 자동매매시작\n보유자산 : {est_balance}"
        self.record(msg)

        msg = '\n'.join((msg, f'잔액 : {current_balance}'))

        # Target price for each ticker
        for buy_margin in self.buy_margins:
            msg = '\n'.join((msg, f"[{buy_margin.ticker}]", f"Target Price: {buy_margin.target_price}"))

        self.message(msg)
        
        # Set the reset time
        now = datetime.now()
        now = datetime(year = now.year, month = now.month, day = now.day, hour = now.hour)
        self.reset_time = now + timedelta(days=1)

        while self.reset_time.hour != self.reset_hour:
            self.reset_time = self.reset_time - timedelta(hours = 1)
        

        # Run
        while self.working:
            try:

                # If at hold status, continue
                if self.hold_tr:
                    time.sleep(2)
                    continue
                
                # Get current time
                now = datetime.now()

                # Reset and sell all
                if now >= self.reset_time:

                    # Indicate the reset
                    current_time = now.strftime("%Y/%m/%d %H:%M")
                    msg = (f"--[{current_time}]-- Reset")

                    for buy_margin in self.buy_margins:
                        
                        # If bought, sell
                        if buy_margin.bought:
                            sell_all(self.account, buy_margin.ticker)
                            msg = '\n'.join((msg, f"{buy_margin.ticker} 매도"))
                        
                        # Reset the target prices
                        buy_margin.set_new_target(now.hour)

                        time.sleep(2)
                    
                    self.message(msg)
                    self.record(msg)

                    # New reset time
                    now = datetime(year = now.year, month = now.month, day = now.day, hour = now.hour)
                    self.reset_time = now + timedelta(days = 1)

                    # Starting balance
                    current_balance = self.account.get_balance()
                    est_balance = self.account.get_estimated_balance()
                    msg = f"보유자산 : {est_balance}"
                    self.record(msg)

                    msg = '\n'.join((msg, f'잔액 : {current_balance}'))
                    
                    # Print target price for each ticker
                    for buy_margin in self.buy_margins:
                        msg = '\n'.join((msg, f"[{buy_margin.ticker}]", f"Target Price: {buy_margin.target_price}"))

                    self.message(msg)

                # Get current prices
                current_prices = UpbitQuotationAPI.get_current_prices(self.tickers)

                # Check the buy margin
                for buy_margin in self.buy_margins:
                    
                    # If bought already, continue
                    if buy_margin.bought:
                        continue

                    ticker = buy_margin.ticker
                    current_price = current_prices[ticker]
                    
                    # Buy condition
                    if buy_margin.should_i_buy(current_price):
                        betting_ratio = get_betting_ratio(ticker, current_price) * self.betting
                        buy_price = betting_ratio * current_balance / len(self.tickers)
                        buy_set_price(self.account, ticker, buy_price)

                        current_time = now.strftime("%Y/%m/%d %H:%M")
                        msg = f"--[{current_time}]--\n{ticker} 매수\n매수 금액 : {buy_price}"

                        self.message(msg)
                        self.record(msg)
                        
                time.sleep(2)
            except:
                current_time = datetime.now()
                current_time = current_time.strftime("%Y/%m/%d %H:%M")
                msg = f"--[{current_time}]-- Error"
                self.message(msg)
                self.record(msg)
                time.sleep(5)
        
        self.message('Trading stopped')


    def end(self):
        self.working = False

    def reset(self):
        self.reset_time = datetime.now()

    def extend(self):
        self.reset_time = self.reset_time + timedelta(days = 1)
        reset_time = self.reset_time.strftime("%Y/%m/%d %H:%M")
        msg = f"Reset Time Extended : {reset_time}"
        self.message(msg)
    
    def hold(self):
        self.hold_tr = True
        msg = '-- HOLD --'
        self.message(msg)

    def release(self):
        self.hold_tr = False
        msg = '-- RELEASE --'
        self.message(msg)
        
    def set_tickers(self, string):
        if self.working:
            self.message('You can\'t change settings when trading is running.')
        else:
            try:
                tickers = UpbitQuotationAPI.get_tickers()
                ls = string.split()
                if len(ls) == 0:
                    self.message('You need to have at least one ticker name.')
                    raise Exception
                result = []
                for i in ls:
                    ticker = string_to_ticker(i)
                    if ticker in tickers:
                        result.append(ticker)
                    else:
                        self.message(f'\'{i}\' is not a valid ticker name.')
                        raise Exception
                self.tickers = result
                self.message('Success')
            except:
                self.message('Error')

    def set_ratio(self, ratio):
        if self.working:
            self.message('You can\'t change settings when trading is running.')
        else:
            try:
                ratio = float(ratio)
                if 0 < ratio < 1:
                    self.betting = ratio
                else:
                    self.message('The value has to be in between 0 and 1.')
                    raise Exception
                self.message('Success')
            except:
                self.message('Error')