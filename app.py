from src.main.controller import controller
from src.resources.commands import get_commands
from src.rise_alert import rise_alert_thread
from src.upbit import upbit_exchange_api
from src.telesk import Telesk
import logging.config
import json
from env import access_key, secret_key, api_key, user_id, is_production
import os

if is_production:
    if not os.path.exists('./logs'):
        os.mkdir('./logs')
    logging.config.dictConfig(json.load(open('./logger.json')))
else:
    logging.config.dictConfig(json.load(open('./logger.dev.json')))

upbit_exchange_api.config(access_key, secret_key)

app = Telesk()
app.config['api_key'] = api_key
app.config['one_user'] = user_id
app.config['commands'] = get_commands()
app.config['allow_group'] = False
app.register_blueprint(controller)

if __name__ == '__main__':
    rise_alert_thread.start()
    app.poll()
