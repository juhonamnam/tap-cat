from .base import controller


@controller.route('/action')
def start_command(chat_id, args, msg_info):
    pass


@controller.route('buy', type='callback')
def buy_callback(chat_id, msg_id, args, callback_info):
    pass


@controller.route('sell', type='callback')
def sell_callback(chat_id, msg_id, args, callback_info):
    pass


@controller.route('random_game', type='callback')
def random_game_callback(chat_id, msg_id, args, callback_info):
    pass
