from .base import controller
from src.main import service


@controller.route('/action')
def start_command(chat_id, args, msg_info):
    msg_id = msg_info['message_id']
    service.action_service(chat_id, msg_id)


@controller.route('action', type='callback')
def buy_callback(chat_id, msg_id, args, callback_info):
    service.action_service(chat_id, msg_id, callback=True)


@controller.route('buy_page', type='callback')
def buy_callback(chat_id, msg_id, args, callback_info):
    offset = int(args[0])
    service.buy_page_service(chat_id, msg_id, offset)


@controller.route('sell', type='callback')
def sell_callback(chat_id, msg_id, args, callback_info):
    pass


@controller.route('random_game', type='callback')
def random_game_callback(chat_id, msg_id, args, callback_info):
    pass
