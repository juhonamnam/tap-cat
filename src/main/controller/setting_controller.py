from .base import controller
from src.main import service


@controller.route('/setting')
def setting_command(chat_id, args, msg_info):
    msg_id = msg_info['message_id']
    service.setting_service(chat_id, msg_id)


@controller.route('setting', type='callback')
def setting_callback(chat_id, msg_id, args, callback_info):
    service.setting_service(chat_id, msg_id, callback=True)


@controller.route('rise_alert', type='callback')
def rise_alert_callback(chat_id, msg_id, args, callback_info):
    service.rise_alert_service(chat_id, msg_id)


@controller.route('set_rise_alert', type='callback')
def set_rise_alert_callback(chat_id, msg_id, args, callback_info):
    callback_query_id = callback_info['id']
    service.set_rise_alert_service(chat_id, args[0], msg_id, callback_query_id)
