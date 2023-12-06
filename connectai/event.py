import logging
import asyncio
from flask import Flask, request, jsonify
from functools import partial, wraps
from .globals import current_broker, _cv_broker, broker_ctx, _cv_instance
from .ctx import InstanceContext
from .message import Message


class BaseEventHandler(InstanceContext):

    def __init__(self, app_id='noop'):
        super().__init__()
        self.app_id = app_id
        current_broker.register_event(self)

    async def start(self, *args, **kwargs):
        raise NotImplementedError


class FeishuCallbackHandler(BaseEventHandler):

    def __init__(self, app_id='noop', prefix='/api/feishu', port=8888):
        super().__init__(app_id)
        self.prefix = prefix
        self.port = port

    def get_app(self):
        app = Flask(__name__)
        # save broker_ctx in current scope
        broker_ctx = _cv_broker.get(None)

        def event_handler(app_id):
            bot = broker_ctx.broker.get_bot(app_id)
            if bot:
                message = bot.parse_message(request)
                if message and bot.filter(message):
                    broker_ctx.broker.bot_queue.put_nowait((app_id, message))
                if 'challenge' in message:
                    return jsonify(message)
            return ''

        app.add_url_rule(f"{self.prefix}/<app_id>", 'event_handler', event_handler, methods=['POST'])
        return app

    async def start(self, port=None):
        app = self.get_app()
        app.run(port=port or self.port)


class NoopEventHandler(BaseEventHandler):

    async def start(self):
        while True:
            content = input('User: ')
            message = self.parse_message(content)
            current_broker.bot_queue.put_nowait((self.app_id, message))
            await asyncio.sleep(0.1)

    def parse_message(self, content):
        return Message(app_id=self.app_id, content=content)

