from src.resources.message import get_message
from .base import controller


@controller.route('/start')
def start_command(chat_id, args, msg_info):
    msg_id = msg_info['message_id']
    controller.delete_message_thread(chat_id, msg_id)
    controller.send_message_with_dict({
        'chat_id': chat_id,
        'text': get_message()('start.default')
    })


@controller.route('exit', type='callback')
def exit_callback(chat_id, msg_id, args, callback_info):
    controller.delete_message(chat_id, msg_id)
