import requests
import json

def getMe(token):
    
    try:
        url = f'https://api.telegram.org/bot{token}/getMe'

        querystring = {}

        headers = {"Accept": "application/json"}

        response = requests.request("GET", url, headers=headers, params = querystring)

        return response.json()

    except Exception as x:
        print(x.__class__.__name__)
        return None

def sendMessage(token, chat_id, text):
    
    try:
        url = f'https://api.telegram.org/bot{token}/sendMessage'

        querystring = {'chat_id': chat_id, 'text': text}

        headers = {"Accept": "application/json"}

        response = requests.request("GET", url, headers=headers, params = querystring)

        return response.json()

    except Exception as x:
        print(x.__class__.__name__)
        return None

def sendMessageKeyboardButtons(token, chat_id, text, reply_markup):
    
    try:
        url = f'https://api.telegram.org/bot{token}/sendMessage'

        querystring = {'chat_id': chat_id, 'text': text, 'reply_markup': json.dumps(reply_markup)}

        headers = {"Accept": "application/json"}

        response = requests.request('POST',url, headers=headers, params = querystring)

        return response.json()

    except Exception as x:
        print(x.__class__.__name__)
        return None


def setMyCommands(token, commands):
    
    try:
        url = f'https://api.telegram.org/bot{token}/setMyCommands'

        querystring = {'commands' : json.dumps(commands)}

        headers = {"Accept": "application/json"}

        response = requests.request('POST',url, headers=headers, params = querystring)

        return response.json()

    except Exception as x:
        print(x.__class__.__name__)
        return None
