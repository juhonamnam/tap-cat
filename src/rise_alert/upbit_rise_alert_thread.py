import threading
import time
from src.resources import get_message
from src.upbit import upbit_exchange_api, upbit_quotation_api
from src.main.controller.base import controller
import logging


class RiseAlertThread(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.sell_alert = dict()
        self.thread_alive = True
        self.thread_active = False
        self.daemon = True
        self.logger = logging.getLogger('rise_alert')

    def run(self):
        self.thread_active = True

        while self.thread_alive:
            if self.thread_active:
                try:
                    balances = upbit_exchange_api.get_balances(
                        method='avg_buy_price')
                    if not balances['ok']:
                        raise Exception(balances['description'])

                    avg_buy_prices = balances['data']

                    valid_tickers = avg_buy_prices.keys()

                    curr_prices = upbit_quotation_api.get_current_prices(
                        valid_tickers)
                    if not curr_prices['ok']:
                        raise Exception(curr_prices['description'])

                    curr_time = time.time()

                    for ticker in self.sell_alert.copy():
                        if ticker not in valid_tickers:
                            del self.sell_alert[ticker]

                    for ticker in valid_tickers:
                        intr = float(curr_prices['data'][ticker]) / \
                            float(avg_buy_prices[ticker]) - 1
                        intr = intr * 100

                        if ticker in self.sell_alert and self.sell_alert[ticker]['time'] + 1800 < curr_time and self.sell_alert[ticker]['interest'] > intr:
                            del self.sell_alert[ticker]

                        if ticker not in self.sell_alert and intr >= 5:
                            self.sell_alert[ticker] = {
                                'time': curr_time,
                                'interest': (intr // 5) * 5
                            }
                            self._send_alert(
                                ticker, self.sell_alert[ticker]['interest'])

                        elif ticker in self.sell_alert and intr >= self.sell_alert[ticker]['interest'] + 5:
                            self.sell_alert[ticker] = {
                                'time': curr_time,
                                'interest': (intr // 5) * 5
                            }
                            self._send_alert(
                                ticker, self.sell_alert[ticker]['interest'])

                except Exception as e:
                    self.logger.exception(e)
                    time.sleep(5)

            time.sleep(2)

        self.thread_active = False

    def end(self):
        self.thread_alive = False

    def set_active_status(self, activity: bool):
        self.thread_active = activity

    def _send_alert(self, ticker, intr):
        controller.send_message_with_dict({
            'chat_id': controller.config['one_user'],
            'text': get_message()('rise_alert').format(ticker=ticker, intr=intr)
        })
