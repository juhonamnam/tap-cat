import time
from src.resources import get_message
from src.main.controller.base import controller
from src.upbit import upbit_quotation_api, upbit_exchange_api
import json
import random


def action_service(chat_id, msg_id, callback=False):
    text = get_message()('action.default')
    inline_keyboard = [
        [{'text': get_message()('action.buy'), 'callback_data': 'buy_page 0'},
         {'text': get_message()('action.sell'), 'callback_data': 'sell_page 0'}],
        [{'text': get_message()('action.rg'), 'callback_data': 'random_game'}],
        [{'text': get_message()('com.exit'), 'callback_data': 'exit'}],
    ]

    if callback:
        controller.edit_message_with_dict({
            'message_id': msg_id,
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'HTML',
            'reply_markup': json.dumps({
                'inline_keyboard': inline_keyboard
            })

        })
        return

    controller.delete_message_thread(chat_id, msg_id)
    controller.send_message_with_dict({
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML',
        'reply_markup': json.dumps({
            'inline_keyboard': inline_keyboard
        })
    })


def buy_page_service(chat_id, msg_id, offset=0, limit=18, row=6):
    tickers_info = upbit_quotation_api.get_tickers(
        method='paging', offset=offset, limit=limit)

    if not tickers_info['ok']:
        controller.edit_message_with_dict({
            'message_id': msg_id,
            'chat_id': chat_id,
            'text': get_message()('com.error').format(description=tickers_info['description']),
            'reply_markup': json.dumps({
                'inline_keyboard': [[{'text': get_message()('com.retry'), 'callback_data': f'buy_page {offset}'}],
                                    [{'text': get_message()('com.exit'), 'callback_data': 'exit'}]]
            }),
        })

        return

    inline_keyboard = []

    ticker_list = tickers_info['data']['list']

    for i in range(limit-len(ticker_list)):
        ticker_list.append(None)

    col = int(limit / row)

    for i in range(row):
        row = list()
        for ticker in ticker_list[i*col: i*col+col]:
            if ticker:
                row.append({'text': ticker, 'callback_data': 'buy ' + ticker})
            else:
                row.append({'text': ' ', 'callback_data': f'dummy_callback'})

        inline_keyboard.append(row)

    total = tickers_info["data"]["paginate"]["total"]

    max_page = (total - 1) // limit
    if max_page > 0 or offset != 0:
        pager_link = list()
        block_page = offset // 5

        if block_page != 0:
            pager_link.append(
                {'text': '<<', 'callback_data': 'buy_page 0'})
            pager_link.append(
                {'text': '<', 'callback_data': f'buy_page {(block_page) * 5 - 1}'})

        for _offset in range(block_page * 5, min(block_page * 5 + 5, max_page + 1)):
            if _offset == offset:
                pager_link.append(
                    {'text': f'({_offset + 1})', 'callback_data': f'buy_page {_offset}'})
            else:
                pager_link.append(
                    {'text': f'{_offset + 1}', 'callback_data': f'buy_page {_offset}'})

        if block_page != max_page // 5:
            pager_link.append(
                {'text': '>', 'callback_data': f'buy_page {(block_page) * 5 + 5}'})
            pager_link.append(
                {'text': '>>', 'callback_data': f'buy_page {max_page}'})

        inline_keyboard.append(pager_link)

    inline_keyboard.append(
        [{'text': get_message()('com.exit'), 'callback_data': 'exit'}])

    controller.edit_message_with_dict({
        'message_id': msg_id,
        'chat_id': chat_id,
        'text': get_message()('action.buy.pg_text').format(total=total, page=offset + 1),
        'reply_markup': json.dumps({
            'inline_keyboard': inline_keyboard
        }),
        'parse_mode': 'HTML',
    })


def sell_page_service(chat_id, msg_id, offset=0, limit=18, row=6):
    tickers_info = upbit_exchange_api.get_balances(
        method='paging', offset=offset, limit=limit)

    if not tickers_info['ok']:
        controller.edit_message_with_dict({
            'message_id': msg_id,
            'chat_id': chat_id,
            'text': get_message()('com.error').format(description=tickers_info['description']),
            'reply_markup': json.dumps({
                'inline_keyboard': [[{'text': get_message()('com.retry'), 'callback_data': f'sell_page {offset}'}],
                                    [{'text': get_message()('com.exit'), 'callback_data': 'exit'}]]
            }),
        })

        return

    inline_keyboard = []

    ticker_list = tickers_info['data']['list']

    for i in range(limit-len(ticker_list)):
        ticker_list.append(None)

    col = int(limit / row)

    for i in range(row):
        row = list()
        for ticker in ticker_list[i*col: i*col+col]:
            if ticker:
                row.append({'text': ticker, 'callback_data': 'sell ' + ticker})
            else:
                row.append({'text': ' ', 'callback_data': f'dummy_callback'})

        inline_keyboard.append(row)

    total = tickers_info["data"]["paginate"]["total"]

    max_page = (total - 1) // limit
    if max_page > 0 or offset != 0:
        pager_link = list()
        block_page = offset // 5

        if block_page != 0:
            pager_link.append(
                {'text': '<<', 'callback_data': 'sell_page 0'})
            pager_link.append(
                {'text': '<', 'callback_data': f'sell_page {(block_page) * 5 - 1}'})

        for _offset in range(block_page * 5, min(block_page * 5 + 5, max_page + 1)):
            if _offset == offset:
                pager_link.append(
                    {'text': f'({_offset + 1})', 'callback_data': f'sell_page {_offset}'})
            else:
                pager_link.append(
                    {'text': f'{_offset + 1}', 'callback_data': f'sell_page {_offset}'})

        if block_page != max_page // 5:
            pager_link.append(
                {'text': '>', 'callback_data': f'sell_page {(block_page) * 5 + 5}'})
            pager_link.append(
                {'text': '>>', 'callback_data': f'sell_page {max_page}'})

        inline_keyboard.append(pager_link)

    inline_keyboard.append(
        [{'text': get_message()('com.exit'), 'callback_data': 'exit'}])

    controller.edit_message_with_dict({
        'message_id': msg_id,
        'chat_id': chat_id,
        'text': get_message()('action.sell.pg_text').format(total=total, page=offset + 1),
        'reply_markup': json.dumps({
            'inline_keyboard': inline_keyboard
        }),
        'parse_mode': 'HTML',
    })


def buy_price_input_service(chat_id, msg_id, ticker):
    controller.delete_message_thread(chat_id, msg_id)
    controller.send_message_with_dict({
        'chat_id': chat_id,
        'text': get_message()('action.buy_input_text').format(ticker=ticker),
        'reply_markup': json.dumps({
            'force_reply': True,
            'input_field_placeholder': ticker,
        }),
        'parse_mode': 'HTML',
    })


def sell_price_input_service(chat_id, msg_id, ticker):
    balance = upbit_exchange_api.get_balances(method='single', ticker=ticker)

    if not balance['ok']:
        controller.edit_message_with_dict({
            'message_id': msg_id,
            'chat_id': chat_id,
            'text': get_message()('com.error').format(description=balance['description']),
            'reply_markup': json.dumps({
                'inline_keyboard': [[{'text': get_message()('com.retry'), 'callback_data': f'sell {ticker}'}],
                                    [{'text': get_message()('com.exit'), 'callback_data': 'exit'}]]
            }),
        })
        return

    curr_price = upbit_quotation_api.get_current_prices(
        tickers=ticker, method='single')

    if not curr_price['ok']:
        controller.edit_message_with_dict({
            'message_id': msg_id,
            'chat_id': chat_id,
            'text': get_message()('com.error').format(description=curr_price['description']),
            'reply_markup': json.dumps({
                'inline_keyboard': [[{'text': get_message()('com.retry'), 'callback_data': f'sell {ticker}'}],
                                    [{'text': get_message()('com.exit'), 'callback_data': 'exit'}]]
            }),
        })
        return

    curr_balance = float(balance['data']['balance'])

    calculated_value = curr_balance * \
        curr_price['data']['trade_price']

    controller.delete_message_thread(chat_id, msg_id)
    controller.send_message_with_dict({
        'chat_id': chat_id,
        'text': get_message()('action.sell_input_text').format(ticker=ticker, curr_balance=curr_balance, calculated_value=calculated_value),
        'reply_markup': json.dumps({
            'force_reply': True,
            'input_field_placeholder': ticker,
        }),
        'parse_mode': 'HTML',
    })


def random_game_input_service(chat_id, msg_id):
    controller.delete_message_thread(chat_id, msg_id)
    controller.send_message_with_dict({
        'chat_id': chat_id,
        'text': get_message()('action.rg_input_text'),
        'reply_markup': json.dumps({
            'force_reply': True,
            'input_field_placeholder': get_message()('action.rg_input_ph'),
        }),
        'parse_mode': 'HTML',
    })


def buy_service(chat_id, msg_id, reply_msg_id, ticker, price):
    controller.delete_message_thread(chat_id, msg_id)
    controller.delete_message_thread(chat_id, reply_msg_id)

    try:
        price = int(price)
    except ValueError:
        controller.send_message_with_dict({
            'chat_id': chat_id,
            'text': get_message()('com.error').format(description=get_message()('action.val1')),
            'reply_markup': json.dumps({
                'inline_keyboard': [[{'text': get_message()('com.retry'), 'callback_data': f'buy {ticker}'}],
                                    [{'text': get_message()('com.exit'), 'callback_data': 'exit'}]]
            }),
        })
        return

    if price < 5000:
        controller.send_message_with_dict({
            'chat_id': chat_id,
            'text': get_message()('com.error').format(description=get_message()('action.val2')),
            'reply_markup': json.dumps({
                'inline_keyboard': [[{'text': get_message()('com.retry'), 'callback_data': f'buy {ticker}'}],
                                    [{'text': get_message()('com.exit'), 'callback_data': 'exit'}]]
            }),
        })
        return

    result = upbit_exchange_api.buy_market_order_fee_included(ticker, price)

    if not result['ok']:
        controller.send_message_with_dict({
            'chat_id': chat_id,
            'text': get_message()('com.error').format(description=result['description']),
            'reply_markup': json.dumps({
                'inline_keyboard': [[{'text': get_message()('com.retry'), 'callback_data': f'buy {ticker}'}],
                                    [{'text': get_message()('com.exit'), 'callback_data': 'exit'}]]
            }),
        })
        return

    controller.send_message_with_dict({
        'chat_id': chat_id,
        'text': get_message()('buy.success').format(ticker=ticker)
    })


def sell_service(chat_id, msg_id, reply_msg_id, ticker, price):
    controller.delete_message_thread(chat_id, msg_id)
    controller.delete_message_thread(chat_id, reply_msg_id)

    if price == 'all':
        result = upbit_exchange_api.sell_market_order_all(ticker)

        if not result['ok']:
            controller.send_message_with_dict({
                'chat_id': chat_id,
                'text': get_message()('com.error').format(description=result['description']),
                'reply_markup': json.dumps({
                    'inline_keyboard': [[{'text': get_message()('com.retry'), 'callback_data': f'sell {ticker}'}],
                                        [{'text': get_message()('com.exit'), 'callback_data': 'exit'}]]
                }),
            })
            return

    else:
        try:
            price = int(price)
        except ValueError:
            controller.send_message_with_dict({
                'chat_id': chat_id,
                'text': get_message()('com.error').format(description=get_message()('action.val1')),
                'reply_markup': json.dumps({
                    'inline_keyboard': [[{'text': get_message()('com.retry'), 'callback_data': f'sell {ticker}'}],
                                        [{'text': get_message()('com.exit'), 'callback_data': 'exit'}]]
                }),
            })
            return

        if price < 5000:
            controller.send_message_with_dict({
                'chat_id': chat_id,
                'text': get_message()('com.error').format(description=get_message()('action.val2')),
                'reply_markup': json.dumps({
                    'inline_keyboard': [[{'text': get_message()('com.retry'), 'callback_data': f'sell {ticker}'}],
                                        [{'text': get_message()('com.exit'), 'callback_data': 'exit'}]]
                }),
            })
            return

        result = upbit_exchange_api.sell_market_order_fee_included(
            ticker, price)

        if not result['ok']:
            controller.send_message_with_dict({
                'chat_id': chat_id,
                'text': get_message()('com.error').format(description=result['description']),
                'reply_markup': json.dumps({
                    'inline_keyboard': [[{'text': get_message()('com.retry'), 'callback_data': f'sell {ticker}'}],
                                        [{'text': get_message()('com.exit'), 'callback_data': 'exit'}]]
                }),
            })
            return

    controller.send_message_with_dict({
        'chat_id': chat_id,
        'text': get_message()('sell.success').format(ticker=ticker)
    })


def random_game_service(chat_id, msg_id, reply_msg_id, text: str):
    controller.delete_message_thread(chat_id, msg_id)
    controller.delete_message_thread(chat_id, reply_msg_id)

    args = text.split(' ')
    if len(args) < 2:
        controller.send_message_with_dict({
            'chat_id': chat_id,
            'text': get_message()('com.error').format(description=get_message()('action.val3')),
            'reply_markup': json.dumps({
                'inline_keyboard': [[{'text': get_message()('com.retry'), 'callback_data': 'random_game'}],
                                    [{'text': get_message()('com.exit'), 'callback_data': 'exit'}]]
            }),
        })
        return

    try:
        select = int(args[0])
        price = int(args[1])
    except ValueError:
        controller.send_message_with_dict({
            'chat_id': chat_id,
            'text': get_message()('com.error').format(description=get_message()('action.val4')),
            'reply_markup': json.dumps({
                'inline_keyboard': [[{'text': get_message()('com.retry'), 'callback_data': 'random_game'}],
                                    [{'text': get_message()('com.exit'), 'callback_data': 'exit'}]]
            }),
        })
        return

    if select < 1:
        controller.send_message_with_dict({
            'chat_id': chat_id,
            'text': get_message()('com.error').format(description=get_message()('action.val5')),
            'reply_markup': json.dumps({
                'inline_keyboard': [[{'text': get_message()('com.retry'), 'callback_data': 'random_game'}],
                                    [{'text': get_message()('com.exit'), 'callback_data': 'exit'}]]
            }),
        })
        return

    if price < 5000:
        controller.send_message_with_dict({
            'chat_id': chat_id,
            'text': get_message()('com.error').format(description=get_message()('action.val2')),
            'reply_markup': json.dumps({
                'inline_keyboard': [[{'text': get_message()('com.retry'), 'callback_data': 'random_game'}],
                                    [{'text': get_message()('com.exit'), 'callback_data': 'exit'}]]
            }),
        })
        return

    tickers_info = upbit_quotation_api.get_tickers(method='list')

    if not tickers_info['ok']:
        controller.send_message_with_dict({
            'chat_id': chat_id,
            'text': get_message()('com.error').format(description=tickers_info['description']),
            'reply_markup': json.dumps({
                'inline_keyboard': [[{'text': get_message()('com.retry'), 'callback_data': 'random_game'}],
                                    [{'text': get_message()('com.exit'), 'callback_data': 'exit'}]]
            }),
        })
        return

    choices = random.choices(tickers_info['data'], k=select)

    rows = []

    for ticker in choices:
        result = upbit_exchange_api.buy_market_order_fee_included(
            ticker, price)
        if result['ok']:
            rows.append(get_message()('buy.success').format(ticker=ticker))
        else:
            rows.append(get_message()('buy.fail').format(ticker=ticker))
        time.sleep(0.5)

    controller.send_message_with_dict({
        'chat_id': chat_id,
        'text': '\n'.join(rows)
    })
