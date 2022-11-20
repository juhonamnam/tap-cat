import json
import requests
import time
from threading import Thread
from .scaffold import Scaffold
import logging


class Telesk(Scaffold):
    def __init__(self):
        super().__init__()

        self.config = dict(
            api_key=None,
            timeout=600,
            cool_down=60,
            commands=[],
            allow_group=True,
            one_user=None
        )
        self.bot_info = dict()
        self._offset = 0
        self.logger = logging.getLogger('telesk')

    def register_blueprint(self, blueprint):
        for cmd in blueprint._commands:
            self._add_command(cmd, blueprint._commands[cmd])
        for data in blueprint._callbacks:
            self._add_callback(data, blueprint._callbacks[data])
        blueprint.send_message = self.send_message
        blueprint.send_message_with_dict = self.send_message_with_dict
        blueprint.send_messages = self.send_messages
        blueprint.edit_message = self.edit_message
        blueprint.edit_message_with_dict = self.edit_message_with_dict
        blueprint.delete_message = self.delete_message
        blueprint.delete_message_thread = self.delete_message_thread
        blueprint.answer_callback_query = self.answer_callback_query
        blueprint.answer_callback_query_with_dict = self.answer_callback_query_with_dict
        blueprint.config = self.config

        for bp in blueprint._blueprints:
            self.register_blueprint(bp)

    def _default_command(self, *args):
        pass

    def _default_callback(self, *args):
        pass

    def _process_new_messages(self, response: dict):
        for msg in response.get('result', []):
            self._offset = max(self._offset, msg['update_id'] + 1)
            process_thread = Thread(
                target=self._process_new_message,
                args=[msg]
            )
            process_thread.start()

    def _process_new_message(self, msg: dict):
        try:
            msg_info = msg.get('message')
            callback_info = msg.get('callback_query')
            if msg_info:
                is_group = msg_info['chat']['type'] == 'group'

                if is_group and not self.config['allow_group']:
                    self.logger.info(
                        f'Message Received (Disallowed by Group Message Config): {str(msg)}')
                    return

                chat_id = msg_info.get('chat', {}).get('id')

                if self.config['one_user'] and self.config['one_user'] != str(chat_id):
                    self.logger.info(
                        f'Message Received (Disallowed by One User Message Config): {str(msg)}')
                    return

                self.logger.info(f'Message Received: {str(msg)}')

                text: str = msg_info.get('text', '')

                if text.startswith('/'):
                    splited = text.split(' ')
                    if len(splited) == 1:
                        cmd = text
                        args = []
                    else:
                        cmd = splited[0]
                        args = splited[1:]

                    if is_group:
                        lt = cmd.split('@')
                        if lt[-1] != self.bot_info['username']:
                            return
                        else:
                            cmd = lt[0]

                    command = self._commands.get(cmd)
                    if command:
                        command(chat_id, args, msg_info)
                    else:
                        self._commands.get('default', self._default_command)(
                            chat_id, text, msg_info)
                else:
                    command = self._commands.get('/')
                    if command:
                        command(chat_id, text, msg_info)
                    else:
                        self._commands.get('default', self._default_command)(
                            chat_id, text, msg_info)

            elif callback_info:
                self.logger.info(f'Callback Received: {str(msg)}')
                data: str = callback_info.get('data', '')
                chat_id = callback_info.get(
                    'message', {}).get('chat', {}).get('id')
                msg_id = callback_info.get(
                    'message', {}).get('message_id', '')
                splited = data.split(' ')
                if len(splited) == 1:
                    cb = data
                    args = []
                else:
                    cb = splited[0]
                    args = splited[1:]
                callback = self._callbacks.get(cb)
                if callback:
                    callback(chat_id, msg_id, args, callback_info)
                else:
                    self._callbacks.get('default', self._default_callback)(
                        chat_id, msg_id, data, callback_info)

            else:
                self.logger.info(f'New Update: {str(msg)}')
        except Exception as e:
            self.logger.error(str(e))

    # Initialize
    def _verify_api_key(self):
        if not self.config['api_key']:
            raise Exception("config api_key is undefined")
        response = self._get_me()
        if not response.get('ok', False):
            raise Exception(response.get('description'))
        self.bot_info = response['result']

    def _set_bot_commands_options(self):
        response = self._set_my_commands(self.config['commands'])
        if not response.get('ok', False):
            raise Exception(response.get('description'))

    def _set_initial_offset(self):
        response = self._get_updates()
        if not response.get('ok', False):
            raise Exception(response.get('description'))
        for msg in response.get('result', []):
            self._offset = max(self._offset, msg.get('update_id', 0)) + 1

    def _poll(self, _poll_timeout, _cooldown):
        while True:
            try:
                response = self._get_updates(_poll_timeout, self._offset)
                if response.get('ok', False) is False:
                    raise Exception(response.get('description'))
                else:
                    self._process_new_messages(response)
            except Exception as e:
                self.logger.error(str(e))
                time.sleep(_cooldown)

    def poll(self, on_disconnect=None):

        try:
            self.logger.info('Telesk Server Getting Ready...')
            self._verify_api_key()
            self._set_bot_commands_options()
            self._set_initial_offset()
            poll_timeout = self.config.get('timeout', 600)
            cooldown = self.config.get('cooldown', 60)
            self.logger.info('Telesk Server Start')
            poll_thread = Thread(
                target=self._poll,
                args=(poll_timeout, cooldown),
                daemon=True
            )
            poll_thread.start()
            while True:
                time.sleep(100000)
        except KeyboardInterrupt:
            if on_disconnect:
                on_disconnect()
            self.logger.info('Telesk Server End')
            exit()
        except Exception as e:
            self.logger.error(str(e))

    # Requests
    def _request(self, method, endpoint, **kwargs):
        base_api = "https://api.telegram.org/bot{api_key}/{endpoint}"
        endpoint = base_api.format(api_key=self.config['api_key'],
                                   endpoint=endpoint)

        try:
            response = method(endpoint,
                              data=kwargs.get('data', None),
                              params=kwargs.get('params', {}),
                              timeout=self.config.get('timeout', 600))

            return response.json()
        except requests.exceptions.ConnectionError:
            return {
                'ok': False,
                'description': 'Connection Error'
            }
        except Exception as e:
            return {
                'ok': False,
                'description': str(e),
            }

    def _get_updates(self, timeout=0, offset=None):
        params = dict(
            timeout=timeout,
            offset=offset,
        )
        return self._request(requests.get, 'getUpdates', params=params)

    def _set_my_commands(self, commands):
        data = dict(
            commands=json.dumps(commands)
        )
        return self._request(requests.post, 'setMyCommands', data=data)

    def _get_me(self):
        return self._request(requests.get, 'getMe')

    def send_message(self, chat_id, text, **kwargs):
        data = dict(
            chat_id=chat_id,
            text=text
        )
        for key in kwargs:
            data[key] = json.dumps(kwargs[key])
        result = self._request(requests.post, 'sendMessage', data=data)
        if result['ok']:
            self.logger.info(f'Send Message: {str(result)}')
        else:
            self.logger.error(
                f'Send Message: Result: {str(result)} Data: {data}')

    def send_message_with_dict(self, data: dict):
        result = self._request(requests.post, 'sendMessage', data=data)
        if result['ok']:
            self.logger.info(f'Send Message: {str(result)}')
        else:
            self.logger.error(
                f'Send Message: Result: {str(result)} Data: {data}')

    def send_messages(self, msgs: list):
        for msg in msgs:
            send_message_thread = Thread(
                target=self.send_message_with_dict,
                args=[msg]
            )
            send_message_thread.start()

    def edit_message(self, chat_id, msg_id, text, **kwargs):
        data = dict(
            chat_id=chat_id,
            message_id=msg_id,
            text=text
        )
        for key in kwargs:
            data[key] = json.dumps(kwargs[key])
        result = self._request(requests.post, 'editMessageText', data=data)
        if result['ok']:
            self.logger.info(f'Edit Message: {str(result)}')
        else:
            self.logger.error(
                f'Edit Message: Result: {str(result)} Data: {data}')

    def edit_message_with_dict(self, data: dict):
        result = self._request(requests.post, 'editMessageText', data=data)
        if result['ok']:
            self.logger.info(f'Edit Message: {str(result)}')
        else:
            self.logger.error(
                f'Edit Message: Result: {str(result)} Data: {data}')

    def delete_message(self, chat_id, msg_id):
        params = dict(
            chat_id=chat_id,
            message_id=msg_id,
        )
        result = self._request(requests.get, 'deleteMessage', params=params)
        if result['ok']:
            self.logger.info(
                f'Delete Message: Result: {str(result)} Params: {params}')
        else:
            self.logger.error(
                f'Delete Message: Result: {str(result)} Params: {params}')

    def delete_message_thread(self, chat_id, msg_id):
        Thread(target=self.delete_message, args=[
               chat_id, msg_id], daemon=True).start()

    def answer_callback_query(self, callback_query_id, text=None, cache_time=None):
        data = dict(
            callback_query_id=callback_query_id,
        )
        if text:
            data['text'] = text
        if cache_time:
            data['cache_time'] = cache_time
        result = self._request(requests.post, 'answerCallbackQuery', data=data)
        if result['ok']:
            self.logger.info(
                f'Answer Callback: Result: {str(result)} Data: {data}')
        else:
            self.logger.error(
                f'Answer Callback: Result: {str(result)} Data: {data}')

    def answer_callback_query_with_dict(self, data: dict):
        result = self._request(requests.post, 'answerCallbackQuery', data=data)
        if result['ok']:
            self.logger.info(
                f'Answer Callback: Result: {str(result)} Data: {data}')
        else:
            self.logger.error(
                f'Answer Callback: Result: {str(result)} Data: {data}')
