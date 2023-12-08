import logging
import queue
import asyncio
from functools import partial
from .globals import current_broker, current_instance, _cv_broker, bot
from .ctx import InstanceContext, BrokerContext, MessageContext


class BaseBroker(InstanceContext):

    def __init__(self):
        self.events = dict()
        super().__init__()

    def broker_context(self):
        return BrokerContext(self)

    def message_context(self, app_id, message):
        return MessageContext(self, app_id, message)

    def _launch_events(self):
        return [asyncio.get_event_loop().create_task(event.start()) for _, event in self.events.items()]

    def register_event(self, event):
        self.events[event.app_id] = event

    def _launch_bot_consumer(self):
        return self._launch_consumer('bot')

    def _launch_sender_consumer(self):
        return self._launch_consumer('message')

    def _launch_consumer(self, typ):
        def worker(queue):
            while True:
                app_id, m = queue.get()
                ctx = self.message_context(app_id, m)
                error = None
                try:
                    try:
                        ctx.push()
                        func = bot.run if 'bot' == typ else bot.send
                        if asyncio.iscoroutinefunction(func):
                            result = asyncio.get_event_loop().run_until_complete(func(m))
                        else:
                            result = func(m)
                        if result and 'bot' == typ:
                            m.update(result=result)
                            logging.info("debug result %r", result)
                            current_broker.message_queue.put_nowait((app_id, m))
                    except Exception as e:
                        error = e
                except:  # noqa: B001
                    error = sys.exc_info()[1]
                    raise
                finally:
                    queue.task_done()
                    ctx.pop(error)

        queue = self.bot_queue if 'bot' == typ else self.message_queue
        return asyncio.get_event_loop().run_in_executor(None, partial(worker, queue))

    def launch(self):
        if _cv_broker.get(None):
            self._launch()
        else:
            with self.broker_context():
                self._launch()


class QueueBroker(BaseBroker):
    def __init__(self, maxsize=0):
        super().__init__()
        self.bot_queue = queue.Queue(maxsize=maxsize)
        self.message_queue = queue.Queue(maxsize=maxsize)
        self.bots = dict()

    def _launch(self):
        tasks = [
            self._launch_bot_consumer(),
            self._launch_sender_consumer(),
            *self._launch_events()
        ]
        asyncio.get_event_loop().run_until_complete(asyncio.wait(tasks))

    def get_bot(self, app_id):
        return self.bots[app_id] if app_id in self.bots else None

    def register_bot(self, bot):
        self.bots[bot.app_id] = bot


MessageBroker = QueueBroker
