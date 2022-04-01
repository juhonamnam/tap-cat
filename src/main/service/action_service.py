from src.resources import get_message
from src.main.controller.base import controller
from src.upbit import upbit_quotation_api
import json


def action_service(chat_id, msg_id, callback=False):
    text = 'Choose Your Action'
    inline_keyboard = [
        [{'text': 'Buy', 'callback_data': 'buy_page 0'},
         {'text': 'Sell', 'callback_data': 'sell_page 0'}],
        [{'text': 'Random Game', 'callback_data': 'random_game'}],
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
            'text': f'Error: {tickers_info["description"]}',
            'reply_markup': json.dumps({
                'inline_keyboard': [[{'text': 'Retry', 'callback_data': f'buy_page {offset}'}],
                                    [{'text': get_message()('com.exit'), 'callback_data': 'exit'}]]
            }),
            'parse_mode': 'HTML',
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
        'text': f'Total: {total}\nCurrent Page: {offset + 1}',
        'reply_markup': json.dumps({
            'inline_keyboard': inline_keyboard
        }),
        'parse_mode': 'HTML',
    })


def buy_price_input_service(chat_id, msg_id, ticker):
    controller.delete_message_thread(chat_id, msg_id)
    controller.send_message_with_dict({
        'chat_id': chat_id,
        'text': f'Order Type: <b>buy</b>\nSelected Ticker: <i>{ticker}</i>\n\nEnter the amount that you want to buy in KRW',
        'reply_markup': json.dumps({
            'force_reply': True,
            'input_field_placeholder': ticker,
        }),
        'parse_mode': 'HTML',
    })


def buy_service(chat_id, msg_id, reply_msg_id, ticker, price):
    controller.delete_message_thread(chat_id, msg_id)
    controller.delete_message_thread(chat_id, reply_msg_id)

    # 매수작업 연동
    controller.send_message_with_dict({
        'chat_id': chat_id,
        'text': f'Ticker: {ticker}\nPrice: {price}'
    })
