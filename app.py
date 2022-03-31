import os
import sys
from src.main.controller import controller
from src.resources.commands import get_commands
from src.rise_alert import rise_alert_thread
from src.upbit import upbit_exchange_api
from src.telesk import Telesk
import logging.config
import json

if len(sys.argv) > 1 and sys.argv[1] == 'dev':
    logging.config.dictConfig(json.load(open('./logger.dev.json')))
else:
    logging.config.dictConfig(json.load(open('./logger.local.json')))

access = os.getenv('cat_upbit_access_key')
secret = os.getenv('cat_upbit_secret_key')

upbit_exchange_api.config(access, secret)

app = Telesk()
app.config['api_key'] = os.getenv('cat_tele_key')
app.config['one_user'] = os.getenv('cat_user_id', 'dummy_user_id')
app.config['commands'] = get_commands()
app.config['allow_group'] = False
app.register_blueprint(controller)

if __name__ == '__main__':
    rise_alert_thread.start()
    app.poll()
