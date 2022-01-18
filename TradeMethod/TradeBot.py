import time
from TradeMethod.AlertThread import AlertThread
from TradeMethod.VBSThread import VBSThread
from UpbitOpenAPI import UpbitQuotationAPI
from UpbitOpenAPI import UpbitExchangeAPI
from TradeMethod.volatility import *
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
