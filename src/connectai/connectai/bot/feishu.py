import json
import logging

from flask import Request

from connectai.lark.sdk import AESCipher
from connectai.lark.sdk import Bot as Client
from connectai.lark.sdk import FeishuBaseMessage, FeishuMessageCard, FeishuTextMessage

from ..message import FeishuEventMessage, MessageType, QueueMessage
from ..storage import BaseStorage, ExpiredDictStorage
from .base import BaseBot


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
        self.on("filter", lambda message: "challenge" not in message.raw)
        self.storage = None

    def run(self, message):
        try:
            if isinstance(message.raw, FeishuEventMessage):
                message_type = message.raw.event.message.message_type
                return self.trigger(message_type, message)
            raise Exception("Unkown message")
        except Exception as e:
            logging.error(e)

    def _decrypt_data(self, encrypt_key, encrypt_data):
        cipher = AESCipher(encrypt_key)
        return json.loads(cipher.decrypt_string(encrypt_data))

    def parse_message(self, message):
        # TODO self.client._validate(self.encrypt_key, {'body': conetne.json})
        if isinstance(message, Request):
            data = message.json
            if "encrypt" in data:
                data = self.client._decrypt_data(self.encrypt_key, data["encrypt"])
            message = FeishuEventMessage(**data)
        typ = MessageType.Unkown
        content = ""
        if isinstance(message, FeishuEventMessage):
            try:
                message_type = message.event.message.message_type.capitalize()
                typ = getattr(MessageType, message_type)
                content = message.event.message.content
            except Exception as e:
                logging.warning(e)
        elif isinstance(message, str):
            typ = MessageType.Text
            content = message
            message = Message(content=content)

        return QueueMessage(typ, content, message)

    def get_message_id(self, message):
        try:
            return message.event.message.message_id
        except Exception as e:
            logging.warning(e)
            return ""

    def get_message_type(self, message, update=False):
        if isinstance(message, FeishuMessageCard):
            return MessageType.UpdateCard if update else MessageType.ReplyCard
        if isinstance(message, FeishuBaseMessage):
            try:
                message_type = message.msg_type.capitalize()
                return getattr(MessageType, message_type)
            except Exception as e:
                logging.warning(e)
        return MessageType.Unkown

    def send(self, message: QueueMessage):
        # logging.error("FeishuChatBot.send %r", message)
        message_id = self.get_message_id(message.raw)
        key = f"reply_id:{message_id}"
        result = {}

        if (
            message.type in (MessageType.ReplyCard, MessageType.UpdateCard)
            and not self.storage
        ):
            self.storage = ExpiredDictStorage()

        if message.type == MessageType.ReplyCard:
            result = self.client.reply(message_id, message.result).json()
            # try save reply_message_id
            if "message_id" in result.get("data", {}):
                self.storage.set(key, result["data"]["message_id"])
        elif message.type == MessageType.UpdateCard:
            if self.storage.has(key):
                result = self.client.update(
                    self.storage.get(key), message.result
                ).json()
            else:
                logging.error("can not get reply_message_id %r", message)
        elif isinstance(message.result, FeishuBaseMessage):
            result = self.client.reply(message_id, message.result).json()
        elif isinstance(message.result, str):
            result = self.client.reply(
                message_id, FeishuTextMessage(message.result)
            ).json()
        # logging.error("FeishuChatBot.result %r", result)
        return result

    def on_new_token(self, fn=None):
        self.on("new_token", fn)

    def on_result(self, fn=None):
        self.on("result", fn)

    def on_text(self, fn=None):
        self.on("text", fn)

    def send_text(self, fn=None):
        self.on("text", fn)
