import asyncio

from flask import Flask, jsonify, request

from connectai.lark.websocket import WS_LARK_PROXY_PROTOCOL, WS_LARK_PROXY_SERVER
from connectai.lark.websocket import Bot as WSBotBase
from connectai.lark.websocket import Client as WSClient

from ..globals import _cv_broker, _cv_instance, broker_ctx, current_broker
from ..message import FeishuEventMessage
from .base import BaseReceiver


class FeishuWebhookReceiver(BaseReceiver):
    def __init__(self, app_id="noop", prefix="/api/feishu", host="0.0.0.0", port=8888):
        super().__init__(app_id)
        self.prefix = prefix
        self.host = host
        self.port = port

    def get_app(self):
        app = Flask(__name__)
        # save broker_ctx in current scope
        broker_ctx = _cv_broker.get(None)

        def webhook_handler(app_id):
            bot = broker_ctx.broker.get_bot(app_id)
            if bot:
                message = bot.parse_message(request)
                if message and bot.filter(message):
                    broker_ctx.broker.bot_queue.put_nowait((app_id, message))
                if "challenge" in message:
                    return jsonify(message.raw)
            return ""

        app.add_url_rule(
            f"{self.prefix}/<app_id>",
            "webhook_handler",
            webhook_handler,
            methods=["POST"],
        )
        return app

    async def start(self, host=None, port=None):
        app = self.get_app()
        app.run(host=host or self.host, port=port or self.port)


class WSFeishuWebsocketReceiver(BaseReceiver):
    def __init__(
        self,
        app_id="noop",
        server=WS_LARK_PROXY_SERVER,
        protocol=WS_LARK_PROXY_PROTOCOL,
    ):
        super().__init__(app_id)
        self.server = server
        self.protocol = protocol

    def get_app(self):
        broker_ctx = _cv_broker.get(None)

        class WSBot(WSBotBase):
            def on_message(self, data, *args, **kwargs):
                bot = broker_ctx.broker.get_bot(self.app_id)
                if bot:
                    message = bot.parse_message(FeishuEventMessage(**data))
                    if bot.filter(message):
                        broker_ctx.broker.bot_queue.put_nowait((self.app_id, message))

        bots = [
            WSBot(
                app_id=bot.app_id,
                app_secret=bot.app_secret,
                verification_token=bot.verification_token,
                encrypt_key=bot.encrypt_key,
            )
            for _, bot in broker_ctx.broker.bots.items()
        ]
        return WSClient(*bots, server=self.server, protocol=self.protocol)

    async def start(self, debug=False):
        app = self.get_app()
        app.start(debug=debug)
