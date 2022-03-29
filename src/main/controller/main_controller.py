from .base import controller
from src.main import service


@controller.route('/start')
def start_command(chat_id, args, msg_info):
    service.start_service(chat_id)


@controller.route('/status')
def start_command(chat_id, args, msg_info):
    service.status_service(chat_id)


@controller.route('/buy')
def start_command(chat_id, args, msg_info):
    try:
        ticker = args[0]
        price = float(args[1])
    except:
        pass


@controller.route('buy', type='callback')
def start_command(chat_id, args, msg_info):
    ticker = args[0]
    price = float(args[1])


@controller.route('/sell')
def start_command(chat_id, args, msg_info):
    try:
        ticker = args[0]
        price = float(args[1])
    except:
        pass


@controller.route('sell', type='callback')
def start_command(chat_id, args, msg_info):
    ticker = args[0]
    price = float(args[1])
