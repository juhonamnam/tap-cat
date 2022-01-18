import threading 
from TradeMethod.volatility import *
import time

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