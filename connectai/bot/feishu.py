import hashlib
import logging
import json
import base64
from Crypto.Cipher import AES
from flask import Request
from .base import BaseBot, Message


class AESCipher(object):
    def __init__(self, key):
        self.bs = AES.block_size
        self.key = hashlib.sha256(AESCipher.str_to_bytes(key)).digest()

    @staticmethod
    def str_to_bytes(data):
        u_type = type(b"".decode("utf8"))
        if isinstance(data, u_type):
            return data.encode("utf8")
        return data

    @staticmethod
    def _unpad(s):
        return s[: -ord(s[len(s) - 1 :])]

    def decrypt(self, enc):
        iv = enc[: AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size :]))

    def decrypt_string(self, enc):
        enc = base64.b64decode(enc)
        return self.decrypt(enc).decode("utf8")


class FeishuChatBot(BaseBot):

    def __init__(self, app_id='', app_secret='', encrypt_key='', verification_token=''):
        super().__init__(app_id)
        self.app_secret = app_secret
        self.encrypt_key = encrypt_key
        self.verification_token = verification_token
        self.on('filter', lambda message: 'challenge' not in message)

    def run(self, message):
        logging.info('FeishuChatBot.run', message)
        # return 'reply ' + message['content']
        return self.trigger('text', message)

    def _decrypt_data(self, encrypt_key, encrypt_data):
        cipher = AESCipher(encrypt_key)
        return json.loads(cipher.decrypt_string(encrypt_data))

    def parse_message(self, content):
        if isinstance(content, Request):
            data = content.json
            if 'challenge' in data:
                return Message(**data)
            if 'encrypt' in data:
                data = self._decrypt_data(self.encrypt_key, data['encrypt'])
            return Message(**data)
        content = content if isinstance(content, str) else str(content)
        return super().parse_message(content)

    def send(self, message):
        logging.info('FeishuChatBot.send', message)

    def send_text(self, fn=None):
        self.on('text', fn)


