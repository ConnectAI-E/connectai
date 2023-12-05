import logging
import asyncio
from inspect import iscoroutinefunction
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
                m = await queue.get()
                ctx = self.message_context(m)
                error = None
                try:
                    try:
                        ctx.push()
                        func = bot.run if 'bot' == typ else bot.send
                        # print('consumer', bot, typ, func, iscoroutinefunction(func))
                        if iscoroutinefunction(func):
                            result = await func(m)
                        else:
                            result = func(m)
                        print('result', func, result, typ)
                        if result and 'bot' == typ:
                            m.update(result=result)
                            current_broker.message_queue.put_nowait(m)
                    except Exception as e:
                        logging.exception(e)
                        error = e
                except Exception as e:  # noqa: B001
                    logging.exception(e)
                    error = sys.exc_info()[1]
                    raise
                finally:
                    queue.task_done()
                    ctx.pop(error)

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
        return self.bots[m.app_id] if m.app_id in self.bots else None

    def register_bot(self, bot):
        self.bots[bot.app_id] = bot


MessageBroker = AsyncQueueBroker
