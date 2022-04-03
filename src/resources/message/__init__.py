from .en import en


def get_message():
    default = 'en'
    messages = {
        'en': en
    }

    return lambda x: messages.get(default, {}).get(x, x)
