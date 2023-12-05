import asyncio
from .globals import current_broker
from .ctx import InstanceContext


class BaseBot(InstanceContext):

    def __init__(self, app_id='', app_secret=''):
        super().__init__()
        self.app_id = app_id
        self.app_secret = app_secret
        current_broker.register_bot(self)


class FeishuChatBot(BaseBot):

    async def run(self, message):
        print('FeishuChatBot.run', message)
        await asyncio.sleep(0.1)
        return 'reply ' + message['content']

    def send(self, message):
        print('FeishuChatBot.send', message)




