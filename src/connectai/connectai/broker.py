import asyncio
import copy
import inspect
import logging
import queue
import sys
from functools import partial

from .ctx import BrokerContext, InstanceContext, MessageContext
from .globals import _cv_broker, bot, current_broker, current_instance


class BaseBroker(InstanceContext):
    def __init__(self):
        self.receivers = dict()
        super().__init__()

    def broker_context(self):
        return BrokerContext(self)

    def message_context(self, app_id, message):
        return MessageContext(self, app_id, message)

    def _launch_receivers(self):
        return [
            asyncio.get_event_loop().create_task(receiver.start())
            for _, receiver in self.receivers.items()
        ]

    def register_receiver(self, receiver):
        self.receivers[receiver.app_id] = receiver

    def _launch_bot_consumer(self):
        return self._launch_consumer("bot")

    def _launch_sender_consumer(self):
        return self._launch_consumer("message")

    def _launch_consumer(self, typ):
        def worker(queue):
            while True:
                app_id, m = queue.get()
                ctx = self.message_context(app_id, m)
                error = None
                try:
                    try:
                        ctx.push()
                        func = bot.run if "bot" == typ else bot.send
                        if asyncio.iscoroutinefunction(func):
                            result = asyncio.get_event_loop().run_until_complete(
                                func(m)
                            )
                        else:
                            result = func(m)
                        if inspect.isgenerator(result):
                            tokens = []
                            replied = False
                            while True:
                                try:
                                    new_token = next(result)
                                    # process streaming new_token
                                    if new_token and "bot" == typ:
                                        tokens.append(new_token)
                                        _m = copy.copy(m)
                                        message, message_type = bot.process_token(
                                            new_token, tokens, update=replied
                                        )
                                        _m.update(
                                            tokens=tokens,
                                            new_token=new_token,
                                            result=message,
                                            type=message_type,
                                        )
                                        current_broker.message_queue.put_nowait(
                                            (app_id, _m)
                                        )
                                        replied = True
                                except StopIteration as e:
                                    # get result value
                                    _m = copy.copy(m)
                                    message, message_type = bot.process_result(
                                        e.value, update=replied
                                    )
                                    _m.update(
                                        tokens=tokens,
                                        result=message,
                                        type=message_type,
                                    )
                                    current_broker.message_queue.put_nowait(
                                        (app_id, _m)
                                    )
                                    break
                                except Exception as e:
                                    logging.exception(e)
                        elif result and "bot" == typ:
                            _m = copy.copy(m)
                            message, message_type = bot.process_result(result)
                            _m.update(result=message, type=message_type)
                            logging.debug("debug result %r", result)
                            current_broker.message_queue.put_nowait((app_id, _m))
                    except Exception as e:
                        logging.exception(e)
                        error = e
                except:  # noqa: B001
                    error = sys.exc_info()[1]
                    raise
                finally:
                    queue.task_done()
                    ctx.pop(error)

        queue = self.bot_queue if "bot" == typ else self.message_queue
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
            *self._launch_receivers(),
        ]
        asyncio.get_event_loop().run_until_complete(asyncio.wait(tasks))

    def get_bot(self, app_id):
        return self.bots[app_id] if app_id in self.bots else None

    def register_bot(self, bot):
        self.bots[bot.app_id] = bot


MessageBroker = QueueBroker
