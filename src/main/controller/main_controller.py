from .base import controller


@controller.route('/start')
def start_command(chat_id, args, msg_info):
    controller.send_message(chat_id, 'testing')


@controller.route('/status')
def start_command(chat_id, args, msg_info):
    pass


@controller.route('/buy')
def start_command(chat_id, args, msg_info):
    pass


@controller.route('/sell')
def start_command(chat_id, args, msg_info):
    pass
