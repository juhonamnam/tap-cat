import json
from src.main import service
from src.resources.message import get_message
from src.upbit import upbit_exchange_api
from .base import controller


@controller.route('ws_sell', type='callback')
def ws_sell_callback(chat_id, msg_id, args, callback_info):
    ticker = args[0]
    result = upbit_exchange_api.sell_market_order_all(ticker)

    if result['ok']:
        controller.edit_message_with_dict({
            'message_id': msg_id,
            'chat_id': chat_id,
            'text': get_message()('sell.success').format(ticker=ticker)
        })

    else:
        controller.edit_message_with_dict({
            'message_id': msg_id,
            'chat_id': chat_id,
            'text': get_message()('com.error').format(description=result['description']),
            'reply_markup': json.dumps({
                'inline_keyboard': [[{'text': get_message()('com.retry'), 'callback_data': f'ws_sell {ticker}'}],
                                    [{'text': get_message()('com.exit'), 'callback_data': 'exit'}]]
            }),
        })
