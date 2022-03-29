from inspect import signature


class Scaffold:
    def __init__(self):
        self._commands = dict()
        self._callbacks = dict()

    def _add_command(self, cmd: str, function, param_length=3):
        if not cmd.startswith('/') and cmd != 'default':
            raise Exception('Command must start with "/"')
        if ' ' in cmd:
            raise Exception('Spacing should not be included in command')
        if cmd in self._commands:
            raise Exception('Duplicate command')
        if param_length > 3:
            raise Exception('Command only takes upto 3 positional argument')
        self._commands[cmd] = function

    def _add_callback(self, data: str, function, param_length=3):
        if ' ' in data:
            raise Exception('Spacing should not be included in callback')
        if data in self._callbacks:
            raise Exception('Duplicate callback')
        if param_length > 4:
            raise Exception('Callback only takes upto 4 positional argument')
        self._callbacks[data] = function

    def route(self, rule: str, type='command'):

        if type == 'callback':
            def decorator(function):
                param_length = len(signature(function).parameters)

                def new_function(*args):
                    function(*args[:param_length])
                self._add_callback(rule, new_function, param_length)
            return decorator

        def decorator(function):
            param_length = len(signature(function).parameters)

            def new_function(*args):
                function(*args[:param_length])
            self._add_command(rule, new_function, param_length)
        return decorator

    def send_message(self, chat_id, text, **kwargs):
        pass

    def send_message_with_dict(self, msg: dict):
        pass

    def send_messages(self, msgs: list):
        pass

    def edit_message(self, chat_id, msg_id, text, **kwargs):
        pass

    def edit_message_with_dict(self, msg: dict):
        pass

    def delete_message(self, chat_id, msg_id):
        pass

    def delete_message_thread(self, chat_id, msg_id):
        pass

    def answer_callback_query(self, callback_query_id, text=None, cache_time=None):
        pass

    def answer_callback_query_with_dict(self, data: dict):
        pass
