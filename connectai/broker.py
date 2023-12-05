import asyncio
from .globals import current_broker, current_instance, _cv_broker, bot
from .ctx import InstanceContext, BrokerContext, MessageContext

class BaseBroker(InstanceContext):

    def __init__(self):
        self.events = dict()
        super().__init__()

    def broker_context(self):
        return BrokerContext(self)

    def message_context(self, message):
        return MessageContext(self, message)

    async def _launch_events(self):
        await asyncio.gather(*[event.start() for _, event in self.events.items()], return_exceptions=True)

    def register_event(self, event):
        self.events[event.app_id] = event

    async def _launch_bot_consumer(self):
        await self._launch_consumer('bot')

    async def _launch_sender_consumer(self):
        await self._launch_consumer('message')

    async def _launch_consumer(self, typ):
        async def worker(queue):
            while True:
                message = await queue.get()
                ctx = self.message_context(message)
                error = None
                try:
                    try:
                        ctx.push()
                        if 'bot' == typ:
                            result = bot.run(message)
                            if result:
                                message.update(result=result)
                                self.message_queue.put_nowait(message)
                        else:
                            bot.send(message)
                    except Exception as e:
                        error = e
                except:  # noqa: B001
                    error = sys.exc_info()[1]
                    raise
                finally:
                    ctx.pop(error)
                    queue.task_done()

        queue = self.bot_queue if 'bot' == typ else self.message_queue
        asyncio.get_event_loop().create_task(worker(queue))

    async def launch(self):
        if _cv_broker.get(None):
            await self._launch()
        else:
            with self.broker_context():
                await self._launch()


class AsyncQueueBroker(BaseBroker):
    def __init__(self, maxsize=0):
        super().__init__()
        self.bot_queue = asyncio.Queue(maxsize=maxsize)
        self.message_queue = asyncio.Queue(maxsize=maxsize)
        self.bots = dict()

    async def _launch(self):
        await self._launch_bot_consumer()
        await self._launch_sender_consumer()
        await self._launch_events()
        for _, event in self.events.items():
            await event.start()

    def get_bot(self, m):
        return self.bots[m['app_id']] if m['app_id'] in self.bots else None

    def register_bot(self, bot):
        self.bots[bot.app_id] = bot


MessageBroker = AsyncQueueBroker
