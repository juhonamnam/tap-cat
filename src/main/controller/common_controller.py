from src.main import service
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


@controller.route('dummy_callback', type='callback')
def setting_command(chat_id, msg_id, args, callback_info):
    controller.answer_callback_query(
        callback_info['id'], cache_time=10000)


@controller.route('/')
def start_command(chat_id, text, msg_info):
    reply = msg_info.get('reply_to_message')

    if not reply:
        return

    reply_text = reply['text']

    action = ''
    arg = ''

    for entity in reply.get('entities', []):
        start = entity['offset']
        end = start + entity['length']
        if entity['type'] == 'bold':
            action = reply_text[start: end]
        elif entity['type'] == 'italic':
            arg = reply_text[start: end]

    if action in ['buy']:
        service.buy_service(
            chat_id, msg_info['message_id'], reply['message_id'], arg, text)

    if action in ['sell']:
        service.sell_service(
            chat_id, msg_info['message_id'], reply['message_id'], arg, text)

    elif action in ['Random Game']:
        service.random_game_service(
            chat_id, msg_info['message_id'], reply['message_id'], text)
