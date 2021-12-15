import threading
import time
from UpbitOpenAPI import UpbitQuotationAPI
from UpbitOpenAPI import UpbitExchangeAPI
from TradeMethod.volatility import *
from datetime import timedelta
from datetime import datetime
from TelegramAPI.telegramAPI import sendMessage, sendMessageKeyboardButtons
import random

class TradeBot:
    def __init__(self, method = 'telegram', tele_info = None):

        self.method = method
        self.tele_info = tele_info
        self.rand_exception = []

        # Get access and secret keys
        try:
            with open("./upbit-key", "r") as f:

                access = f.readline()
                access = access.strip()

                secret = f.readline()
                secret = secret.strip()

            self.account = UpbitExchangeAPI.Account(access, secret)

            if self.account.get_balance('KRW') == None:
                raise Exception()

        # If can't load account, input the access and secret key
        except:
            valid = False
            print('Cannot load your Upbit account.')
            while not valid:
                print('Please insert your access key and secret key of your Upbit account. Once it is validated, this will not be asked again.')
                print('Access Key:')
                access = input()
                print('Secret Key:')
                secret = input()

                self.account = UpbitExchangeAPI.Account(access, secret)

                if self.account.get_balance('KRW') == None:
                    print('Account validation failed.')
                else:
                    print('Success')
                    valid = True

            with open("./upbit-key", "w") as f:
                f.write(f"{access}\n{secret}")
            
        self.volatility = VBSThread(account = self.account, tickers = ["KRW-BTC", "KRW-BCH", "KRW-ETH", 'KRW-EOS'], betting = 0.8, message = self.message, record = self.record)

    def vol_reset(self):
        tickers = self.volatility.tickers
        betting = self.volatility.betting
        self.volatility = VBSThread(account = self.account, tickers = tickers, betting = betting, message = self.message, record = self.record)

    def alert_reset(self):
        self.alert = AlertThread(self.account, self.messageKeyboardButtons)

    def buy(self, ticker, price):
        try:
            ticker = string_to_ticker(ticker)

            status = buy_set_price(self.account, ticker, price)

            if 'error' in status.keys():
                self.message(status['error']['message'])
            else:
                tp = UpbitQuotationAPI.get_current_price(ticker)
                self.message('\n'.join((
                    'Success',
                    f'Transaction Price: {tp}')))

        except:
            self.message("Buy request failed. Check your argument again.")

    def sell(self, ticker, price):
        try:
            ticker = string_to_ticker(ticker)

            if price == 'all':
                status = sell_all(self.account, ticker)
            else:
                status = sell_set_price(self.account, ticker, price)

            if 'error' in status.keys():
                self.message(status['error']['message'])
            else: 
                tp = UpbitQuotationAPI.get_current_price(ticker)
                self.message('\n'.join((
                    'Success',
                    f'Transaction Price: {tp}')))

        except:
            self.message("Sell request failed. Check your argument again.")

    def sell_all(self):
        try:
            balances = self.account.get_balances()
            for balance in balances:
                ticker = string_to_ticker(balance['currency'])
                volume = float(balance['balance'])
                self.account.sell_market_order(ticker, volume)
                time.sleep(0.5)
            self.message('Success')
        except:
            self.message('Error')

    def message(self, text):
        if self.method == 'cmd':
            print(text)
        if self.method == 'telegram':
            bot_token = self.tele_info['bot_token']
            owner_id = self.tele_info['owner_id']
            sendMessage(bot_token, owner_id, text)


    def messageKeyboardButtons(self, text, reply_markup):
        if self.method == 'cmd':
            print(text)
        if self.method == 'telegram':
            bot_token = self.tele_info['bot_token']
            owner_id = self.tele_info['owner_id']
            sendMessageKeyboardButtons(bot_token, owner_id, text, reply_markup)

    def record(self, string):
        with open("./record", "a") as f:
            f.write(string + '\n')

    def random_game(self, k = 4, amount = 10000):
        try:
            tickers = UpbitQuotationAPI.get_tickers(fiat='KRW')

            if self.volatility.working:
                tickers = [x for x in tickers if x not in self.volatility.tickers and x not in self.rand_exception]

            if k > len(tickers):
                self.message('Too many tickers')
            
            elif k * amount > self.account.get_balance():
                self.message('Not enough money')

            elif amount / 1.0005 < 5000:
                self.message('Buy price needs to be above 5000 with the tax included')

            else:

                random_tickers = random.choices(tickers, k=k)
                message = []
                for ticker in random_tickers:
                    status = buy_set_price(self.account, ticker, amount)
                    if 'error' in status.keys():
                        message.append(f'{ticker}: Error') 
                    else:
                        tp = UpbitQuotationAPI.get_current_price(ticker)
                        message.append(f'{ticker}: Success')
                        message.append(f'Transaction Price: {tp}')
                    time.sleep(0.5)
                self.message('\n'.join(message))
        except:
            self.message("Request failed. Check your argument again.")
    
    def add_exception(self, ticker):
        ticker = string_to_ticker(ticker)
        tickers = UpbitQuotationAPI.get_tickers(fiat='KRW')
        if ticker in tickers:
            self.rand_exception.append(ticker)
            self.message('Success')
        else:
            self.message('Such ticker does not exist.')

    def remove_exception(self,ticker):
        ticker = string_to_ticker(ticker)
        if ticker in self.rand_exception:
            self.rand_exception.remove(ticker)
            self.message('Success')
        else:
            self.message('Such ticker is not in the exception list.')


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

class AlertThread(threading.Thread):

    def __init__(self, account, messageKeyboardButtons):
        threading.Thread.__init__(self)
        self.account = account
        self.messageKeyboardButtons = messageKeyboardButtons
        self.sell_alert = dict()
        self.working = False
        self.daemon = True

    def run(self):
        self.working = True

        while self.working:
            try:
                balance = self.account.get_balances()
                avg_buy_prices = {string_to_ticker(x['currency']) : x['avg_buy_price'] for x in balance if x['currency'] != 'KRW'}
                curr_prices = UpbitQuotationAPI.get_current_prices(avg_buy_prices.keys())

                for key in self.sell_alert.copy():
                    if key not in avg_buy_prices:
                        del self.sell_alert[key]

                for ticker in avg_buy_prices:
                    intr = float(curr_prices[ticker]) / float(avg_buy_prices[ticker]) - 1
                    intr = intr * 100
                    if ticker not in self.sell_alert and intr > 5:
                        self.sell_alert[ticker] = ( intr // 5 ) * 5
                        self.alert(ticker, self.sell_alert[ticker])
                    elif ticker in self.sell_alert and intr > self.sell_alert[ticker] + 5:
                        self.sell_alert[ticker] = ( intr // 5 ) * 5
                        self.alert(ticker, self.sell_alert[ticker])

                time.sleep(2)
            except:
                print('Unexpected Error')
                time.sleep(5)

    def end(self):
        self.working = False

    def alert(self, ticker, intr):
        
        msg = '\n'.join((
            f'{ticker} exceeded {intr}%.',
        ))
        
        if self.sell_alert:

            sell_list = [[{'text':f'/sell {x} all'}] for x in self.sell_alert]

            reply_markup = {
                'keyboard' :
                    sell_list,
                'resize_keyboard': True,
            }
            return self.messageKeyboardButtons(msg, reply_markup)
        
        else:
            reply_markup = {
                'remove_keyboard' : True
            }
            return self.messageKeyboardButtons(msg, reply_markup)