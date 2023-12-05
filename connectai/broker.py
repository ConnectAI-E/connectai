import asyncio
from .globals import current_broker, current_instance, _cv_broker
from .ctx import InstanceContext, BrokerContext

class BaseBroker(InstanceContext):

    def __init__(self):
        self.bots = dict()
        super().__init__()

    def broker_context(self):
        return BrokerContext(self)

    def launch(self):
        raise NotImplementedError()

    def get_bot(self, message):
        pass
        # self.bots[message['app_id']] = message

    def register_bot(self, bot):
        self.bots[bot.app_id] = bot

    def launch(self):
        if _cv_broker.get(None):
            self._launch()
        else:
            with self.broker_context():
                self._launch()


class AsyncQueueBroker(BaseBroker):
    def __init__(self, maxsize=0):
        super().__init__()
        self.bot_queue = asyncio.Queue(maxsize=maxsize)
        self.message_queue = asyncio.Queue(maxsize=maxsize)

    def _launch(self):
        print('launch', self.bot_queue, self.message_queue)
        print('current_broker', current_broker)
        print('current_instance', current_instance)
        print('_cv_broker', _cv_broker)


MessageBroker = AsyncQueueBroker
