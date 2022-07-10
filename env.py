import sys
import os

access_key = os.getenv('UPBIT_ACCESS_KEY')
secret_key = os.getenv('UPBIT_SECRET_KEY')
api_key = os.getenv('TELE_KEY')
user_id = os.getenv('TELE_USER_ID')
is_production = len(sys.argv) > 1 and sys.argv[1] == 'production'
