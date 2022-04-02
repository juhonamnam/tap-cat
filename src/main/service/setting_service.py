from src.resources import get_message
from src.main.controller.base import controller
from src.rise_alert import rise_alert_thread
from src.rg_exception import random_game_exception
from src.upbit import upbit_quotation_api
import json


def setting_service(chat_id, msg_id, callback=False):
    ra_status = 'active' if rise_alert_thread.thread_active else 'inactive'
    text = get_message()('setting.default').format(rise_alert=get_message()
                                                   (f'com.{ra_status}'), rg_exception_list=random_game_exception)
    inline_keyboard = [
        [{'text': get_message()('setting.rise_alert'),
          'callback_data': 'rise_alert'},
         {'text': get_message()('setting.rg_exception'),
          'callback_data': 'rg_exception'}],
        [{'text': get_message()('com.exit'),
          'callback_data': 'exit'}],
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


def rise_alert_service(chat_id, msg_id):
    rise_alert = ['active', 'deactivate'] if rise_alert_thread.thread_active else [
        'inactive', 'activate']

    controller.edit_message_with_dict({
        'message_id': msg_id,
        'chat_id': chat_id,
        'text': get_message()(f'rise_alert.default.{rise_alert[0]}'),
        'reply_markup': json.dumps({
            'inline_keyboard': [
                [{'text': get_message()(f'rise_alert.{rise_alert[1]}'),
                  'callback_data': f'set_rise_alert {rise_alert[1]}'}],
                [{'text': get_message()('setting.back'),
                  'callback_data': 'setting'}],
            ]
        }),
        'parse_mode': 'HTML',
    })


def rg_exception_service(chat_id, msg_id):

    controller.edit_message_with_dict({
        'message_id': msg_id,
        'chat_id': chat_id,
        'text': get_message()('rg_exception.default').format(list=random_game_exception),
        'reply_markup': json.dumps({
            'inline_keyboard': [
                [{'text': get_message()('rg_exception.add'), 'callback_data': 'rg_exception_edit add 0'},
                 {'text': get_message()('rg_exception.remove'), 'callback_data': 'rg_exception_edit remove 0'}],
                [{'text': get_message()('setting.back'),
                  'callback_data': 'setting'}],
            ]
        }),
        'parse_mode': 'HTML',
    })


def rg_exception_edit_service(chat_id, msg_id, method, ticker, offset=0, limit=18, row=6):

    if method == 'add':

        if ticker:
            random_game_exception.add(ticker)

        list_info = upbit_quotation_api.get_tickers(
            method='paging', offset=offset, limit=limit, exclude=random_game_exception.set)

        if not list_info['ok']:
            return

    elif method == 'remove':

        if ticker:
            random_game_exception.remove(ticker)

        list_info = {
            'ok': True,
            'data': random_game_exception.paginate(offset, limit)
        }

    if not list_info['ok']:
        controller.edit_message_with_dict({
            'message_id': msg_id,
            'chat_id': chat_id,
            'text': get_message()('com.error').format(description=list_info['description']),
            'reply_markup': json.dumps({
                'inline_keyboard': [[{'text': get_message()('com.retry'), 'callback_data': f'rg_exception_edit {method} {offset}{" " + ticker if ticker else ""}'}],
                                    [{'text': get_message()('com.exit'), 'callback_data': 'exit'}]]
            }),
            'parse_mode': 'HTML',
        })

        return

    inline_keyboard = []

    ticker_list = list_info['data']['list']

    for i in range(limit-len(ticker_list)):
        ticker_list.append(None)

    col = int(limit / row)

    for i in range(row):
        row = list()
        for ticker in ticker_list[i*col: i*col+col]:
            if ticker:
                row.append(
                    {'text': ticker, 'callback_data': f'rg_exception_edit {method} {offset} {ticker}'})
            else:
                row.append({'text': ' ', 'callback_data': f'dummy_callback'})

        inline_keyboard.append(row)

    total = list_info["data"]["paginate"]["total"]

    max_page = (total - 1) // limit
    if max_page > 0 or offset != 0:
        pager_link = list()
        block_page = offset // 5

        if block_page != 0:
            pager_link.append(
                {'text': '<<', 'callback_data': f'rg_exception_edit {method} 0'})
            pager_link.append(
                {'text': '<', 'callback_data': f'rg_exception_edit {method} {(block_page) * 5 - 1}'})

        for _offset in range(block_page * 5, min(block_page * 5 + 5, max_page + 1)):
            if _offset == offset:
                pager_link.append(
                    {'text': f'({_offset + 1})', 'callback_data': f'rg_exception_edit {method} {_offset}'})
            else:
                pager_link.append(
                    {'text': f'{_offset + 1}', 'callback_data': f'rg_exception_edit {method} {_offset}'})

        if block_page != max_page // 5:
            pager_link.append(
                {'text': '>', 'callback_data': f'rg_exception_edit {method} {(block_page) * 5 + 5}'})
            pager_link.append(
                {'text': '>>', 'callback_data': f'rg_exception_edit {method} {max_page}'})

        inline_keyboard.append(pager_link)

    inline_keyboard.append(
        [{'text': get_message()('com.exit'), 'callback_data': 'exit'}])

    controller.edit_message_with_dict({
        'message_id': msg_id,
        'chat_id': chat_id,
        'text': get_message()('rg_exception.default').format(list=random_game_exception),
        'reply_markup': json.dumps({
            'inline_keyboard': inline_keyboard
        }),
        'parse_mode': 'HTML',
    })


def set_rise_alert_service(chat_id, action: str, msg_id, callback_query_id):
    rise_alert_thread.set_active_status(action == 'activate')

    controller.delete_message_thread(chat_id, msg_id)
    controller.answer_callback_query_with_dict({
        'callback_query_id': callback_query_id,
        'text': get_message()('com.success')
    })
