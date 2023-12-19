import json
import logging

from flask import Request

from connectai.lark.sdk import AESCipher
from connectai.lark.sdk import Bot as Client
from connectai.lark.sdk import FeishuBaseMessage, FeishuMessageCard, FeishuTextMessage

from .base import BaseBot, Message


class FeishuChatBot(BaseBot):
    def __init__(self, app_id="", app_secret="", encrypt_key="", verification_token=""):
        super().__init__(app_id)
        self.app_secret = app_secret
        self.encrypt_key = encrypt_key
        self.verification_token = verification_token
        self.client = Client(
            app_id=app_id,
            app_secret=app_secret,
            verification_token=verification_token,
            encrypt_key=encrypt_key,
        )
        self.on("filter", lambda message: "challenge" not in message)

    def run(self, message):
        logging.info("FeishuChatBot.run", message)
        # return 'reply ' + message['content']
        return self.trigger("text", message)

    def _decrypt_data(self, encrypt_key, encrypt_data):
        cipher = AESCipher(encrypt_key)
        return json.loads(cipher.decrypt_string(encrypt_data))

    def parse_message(self, content):
        # TODO self.client._validate(self.encrypt_key, {'body': conetne.json})
        if isinstance(content, Request):
            data = content.json
            if "challenge" in data:
                return Message(**data)
            if "encrypt" in data:
                data = self.client._decrypt_data(self.encrypt_key, data["encrypt"])
            return Message(**data)
        content = content if isinstance(content, str) else str(content)
        return super().parse_message(content)

    def get_message_id(self, message):
        return message.event.message.message_id

    def send(self, message):
        logging.debug("FeishuChatBot.send %r", message)
        message_id = self.get_message_id(message)
        if isinstance(message.result, FeishuMessageCard):
            result = self.client.reply(message_id, message.result).json()
        elif isinstance(message.result, FeishuBaseMessage):
            result = self.client.reply(message_id, message.result).json()
        elif isinstance(message.result, str):
            result = self.client.reply(
                message_id, FeishuTextMessage(message.result)
            ).json()
        else:
            result = {}
        return result.get("data")

    def on_text(self, fn=None):
        self.on("text", fn)

    def send_text(self, fn=None):
        self.on("text", fn)
