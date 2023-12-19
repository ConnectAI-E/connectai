import asyncio

from ..ctx import InstanceContext
from ..globals import current_broker
from ..message import Message


class BaseReceiver(InstanceContext):
    def __init__(self, app_id="noop"):
        super().__init__()
        self.app_id = app_id
        current_broker.register_receiver(self)

    async def start(self, *args, **kwargs):
        raise NotImplementedError


class NoopReceiver(BaseReceiver):
    """
    get input from terminal, and put in bot_queue
    """

    async def start(self):
        while True:
            content = input("User: ")
            message = self.parse_message(content)
            current_broker.bot_queue.put_nowait((self.app_id, message))
            await asyncio.sleep(0.1)

    def parse_message(self, content):
        return Message(app_id=self.app_id, content=content)
