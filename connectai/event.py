import logging
import asyncio
from .globals import current_broker
from .ctx import InstanceContext
from .message import Message


class BaseEventHandler(InstanceContext):

    def __init__(self, app_id):
        super().__init__()
        self.app_id = app_id
        current_broker.register_event(self)

    def start(self, *args, **kwargs):
        raise NotImplementedError


class FeishuCallbackHandler(BaseEventHandler):
    def __init__(self, app_id, verification_token='', encrypt_key=''):
        self.verification_token = verification_token
        self.encrypt_key = encrypt_key
        super().__init__(app_id)


class NoopEventHandler(BaseEventHandler):

    async def start(self):
        while True:
            content = input('User: ')
            current_broker.bot_queue.put_nowait((self.app_id, self.parse_message(content)))
            print('put_nowait', content)
            await asyncio.sleep(0.1)

    def parse_message(self, content):
        return Message(app_id=self.app_id, content=content)


