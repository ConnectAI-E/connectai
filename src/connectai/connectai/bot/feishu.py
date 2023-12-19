import json
import logging

from flask import Request

from connectai.lark.sdk import AESCipher
from connectai.lark.sdk import Bot as Client
from connectai.lark.sdk import FeishuBaseMessage, FeishuMessageCard, FeishuTextMessage

from ..storage import BaseStorage, DictStorage
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
        self.storage = None

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
        logging.error("FeishuChatBot.send %r", message)
        message_id = self.get_message_id(message)
        key = f"reply_id:{message_id}"

        if isinstance(message.result, FeishuMessageCard) and not self.storage:
            self.storage = DictStorage()
        if isinstance(message.result, FeishuMessageCard):
            if self.storage.has(key):
                result = self.client.update(
                    self.storage.get(key), message.result
                ).json()
            else:
                result = self.client.reply(message_id, message.result).json()
            # try save reply_message_id
            # TODO delete reply_message_id
            if not self.storage.has(key) and "message_id" in result.get("data", {}):
                self.storage.set(key, result["data"]["message_id"])
        elif isinstance(message.result, FeishuBaseMessage):
            result = self.client.reply(message_id, message.result).json()
        elif isinstance(message.result, str):
            result = self.client.reply(
                message_id, FeishuTextMessage(message.result)
            ).json()
        else:
            result = {}
        logging.error("FeishuChatBot.result %r", result)
        return result

    def on_new_token(self, fn=None):
        self.on("new_token", fn)

    def on_result(self, fn=None):
        self.on("result", fn)

    def on_text(self, fn=None):
        self.on("text", fn)

    def send_text(self, fn=None):
        self.on("text", fn)
