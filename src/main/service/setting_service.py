from src.resources import get_message
from src.main.controller.base import controller
from src.rise_alert import rise_alert_thread
import json


def setting_service(chat_id, msg_id, callback=False):
    ra_status = 'active' if rise_alert_thread.thread_active else 'inactive'
    text = get_message()('setting.default').format(rise_alert=get_message()
                                                   (f'com.{ra_status}'), rg_exception_list='KRW-EOS')
    inline_keyboard = [
        [{'text': get_message()('setting.rise_alert'),
          'callback_data': 'rise_alert'}],
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


def set_rise_alert_service(chat_id, action: str, msg_id, callback_query_id):
    rise_alert_thread.set_active_status(action == 'activate')

    controller.delete_message_thread(chat_id, msg_id)
    controller.answer_callback_query_with_dict({
        'callback_query_id': callback_query_id,
        'text': get_message()('com.success')
    })
