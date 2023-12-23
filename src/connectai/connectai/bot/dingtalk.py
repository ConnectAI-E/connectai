import json
import logging

from flask import Request

from connectai.dingtalk.sdk import Bot as Client
from connectai.dingtalk.sdk import DingtalkBaseMessage, DingtalkTextMessage

from ..message import DingtalkEventMessage, MessageType, QueueMessage
from .base import BaseBot


class DingtalkChatBot(BaseBot):
    def __init__(self, app_id="", app_secret="", agent_id=""):
        super().__init__(app_id)
        self.app_secret = app_secret
        self.agent_id = agent_id
        self.client = Client(
            app_id=app_id,
            app_secret=app_secret,
            agent_id=agent_id,
        )

    def run(self, message):
        try:
            if isinstance(message.raw, DingtalkEventMessage):
                message_type = message.raw.msgtype
                return self.trigger(message_type, message)
            raise Exception("Unkown message")
        except Exception as e:
            logging.error(e)

    def parse_message(self, message):
        # TODO self.client._validate(self.encrypt_key, {'body': conetne.json})
        if isinstance(message, Request):
            data = message.json
            message = DingtalkEventMessage(**data)
        typ = MessageType.Unkown
        content = ""
        if isinstance(message, DingtalkEventMessage):
            try:
                message_type = message.msgtype.capitalize()
                typ = getattr(MessageType, message_type)
                content = message[message.msgtype]
            except Exception as e:
                logging.warning(e)
        elif isinstance(message, str):
            typ = MessageType.Text
            content = message
            message = Message(content=content)

        return QueueMessage(typ, content, message)

    def get_message_type(self, message):
        if isinstance(message, DingtalkBaseMessage):
            try:
                message_type = message.msgtype.capitalize()
                return getattr(MessageType, message_type)
            except Exception as e:
                logging.warning(e)
        return MessageType.Unkown

    def send(self, message: QueueMessage):
        # logging.error("DingtalkChatBot.send %r", message)
        result = {}
        if isinstance(message.result, DingtalkBaseMessage):
            result = self.client.reply(
                message.raw.sessionWebhook, message.result
            ).json()
        elif isinstance(message.result, str):
            result = self.client.reply(
                message.raw.sessionWebhook, DingtalkTextMessage(message.result)
            ).json()
        # logging.error("DingtalkChatBot.result %r", result)
        return result

    def on_new_token(self, fn=None):
        self.on("new_token", fn)

    def on_result(self, fn=None):
        self.on("result", fn)

    def on_text(self, fn=None):
        self.on("text", fn)

    def send_text(self, fn=None):
        self.on("text", fn)
