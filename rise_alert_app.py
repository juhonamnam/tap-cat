import os
import sys
from src.rise_alert.upbit_rise_alert_thread import RiseAlertThread
from src.telesk import Telesk
import time
import logging.config
import json

if len(sys.argv) > 1 and sys.argv[1] == 'dev':
    logging.config.dictConfig(json.load(open('./logger.main.dev.json')))
else:
    logging.config.dictConfig(json.load(open('./logger.local.json')))

access = os.getenv('cat_upbit_access_key')
secret = os.getenv('cat_upbit_secret_key')

telesk_app = Telesk()
telesk_app.config['api_key'] = os.getenv('cat_tele_key')
telesk_app.config['one_user'] = os.getenv('cat_user_id', 'dummy_user_id')

rise_alert_thread = RiseAlertThread(access, secret, telesk_app=telesk_app)

try:
    while True:
        rise_alert_thread.start()
        time.sleep(100000)
except KeyboardInterrupt:
    exit()
