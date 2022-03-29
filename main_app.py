import os
import sys
from src.telesk import Telesk
from src.main.controller import controller
from src.resources import get_commands
import logging.config
import json

if len(sys.argv) > 1 and sys.argv[1] == 'dev':
    logging.config.dictConfig(json.load(open('./logger.main.dev.json')))
else:
    logging.config.dictConfig(json.load(open('./logger.local.json')))

app = Telesk()
app.config['api_key'] = os.getenv('cat_tele_key')
app.config['one_user'] = os.getenv('cat_user_id', 'dummy_user_id')
app.config['commands'] = get_commands()
app.config['allow_group'] = False
app.register_blueprint(controller)

if __name__ == '__main__':
    app.poll()
