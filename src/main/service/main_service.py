from src.resources import get_message
from src.main.controller.base import controller


def start_service(chat_id):
    controller.send_message_with_dict({
        'chat_id': chat_id,
        'text': get_message()('start.default')
    })


def status_service(chat_id):
    controller.send_message_with_dict({
        'chat_id': chat_id,
        'text': get_message()('status.default').format(rise_alert='ACTIVE', rg_exception_list='KRW-EOS'),
        'parse_mode': 'HTML'
    })
