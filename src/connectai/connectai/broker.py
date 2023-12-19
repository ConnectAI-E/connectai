import asyncio
import inspect
import logging
import queue
import sys
from functools import partial

from .ctx import BrokerContext, InstanceContext, MessageContext
from .globals import _cv_broker, bot, current_broker, current_instance
from .storage import BaseStorage, DictStorage


class BaseBroker(InstanceContext):
    def __init__(self):
        self.receivers = dict()
        self.storage = None
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

    def register_storage(self, storage):
        self.storage = storage

    def _launch_bot_consumer(self):
        return self._launch_consumer("bot")

    def _launch_sender_consumer(self):
        return self._launch_consumer("message")

    def _process_streaming_token(self, bot, m, new_token, tokens, result=None):
        if new_token:
            tokens.append(new_token)
        m.update(tokens=tokens, new_token=new_token)
        if result:
            m.update(result=result)
        # set reply_message_id to message
        if isinstance(self.storage, BaseStorage):
            message_id = bot.get_message_id(m)
            key = f"reply_id:{message_id}"
            print(
                "--------------storage has key",
                self.storage,
                key,
                self.storage.has(key),
            )
            if self.storage.has(key):
                m.update(reply_message_id=self.storage.get(key))
        current_broker.message_queue.put_nowait((bot.app_id, m))

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
                            while True:
                                try:
                                    new_token = next(result)
                                    # process streaming new_token
                                    if new_token and "bot" == typ:
                                        self._process_streaming_token(
                                            bot, m, new_token, tokens
                                        )
                                except StopIteration as e:
                                    # get result value
                                    self._process_streaming_token(
                                        bot, m, None, tokens, e.value
                                    )
                                    break
                                except Exception as e:
                                    logging.exception(e)
                                finally:
                                    if isinstance(self.storage, BaseStorage):
                                        message_id = bot.get_message_id(m)
                                        key = f"reply_id:{message_id}"
                                        if self.storage.has(key):
                                            self.storage.delete(key)
                        elif result and "bot" == typ:
                            m.update(result=result)
                            logging.debug("debug result %r", result)
                            current_broker.message_queue.put_nowait((app_id, m))
                        elif (
                            "message" == typ
                            and isinstance(result, dict)
                            and "message_id" in result
                        ):
                            logging.error("storage %r %r %r", result, self.storage, m)
                            # save reply_message_id in "message" consumer
                            if isinstance(self.storage, BaseStorage):
                                message_id = bot.get_message_id(m)
                                self.storage.set(
                                    f"reply_id:{message_id}", result["message_id"]
                                )
                    except Exception as e:
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
        # set default storage
        if not self.storage:
            DictStorage()
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
