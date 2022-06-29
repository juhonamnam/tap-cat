import sys
from dotenv import load_dotenv
import os

load_dotenv()

access_key = os.getenv('CAT_UPBIT_ACCESS_KEY')
secret_key = os.getenv('CAT_UPBIT_SECRET_KEY')
api_key = os.getenv('CAT_TELE_KEY')
user_id = os.getenv('CAT_USER_ID', 'dummy_user_id')
is_production = len(sys.argv) > 1 and sys.argv[1] == 'production'
