import sys
from .globals import _cv_broker, _cv_instance, _cv_message, current_broker

_sentinel = object()


class BrokerContext:
    def __init__(self, broker, event=None, sender=None):
        self.broker = broker
        self.event = event
        self.sender = sender
        self._cv_tokens = []

    def copy(self):
        return self.__class__(
            self.broker,
            event=self.event,
            sender=self.sender,
        )

    def push(self):
        self._cv_tokens.append(_cv_broker.set(self))

    def pop(self, exc=_sentinel):
        try:
            if len(self._cv_tokens) == 1:
                if exc is _sentinel:
                    exc = sys.exc_info()[1]
                # do_teardown_broker_context(exc)
        finally:
            ctx = _cv_broker.get()
            _cv_broker.reset(self._cv_tokens.pop())
        if ctx is not self:
            raise AssertionError(
                f"Popped wrong broker context. ({ctx!r} instead of {self!r})"
            )

    def __enter__(self):
        self.push()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.pop(exc_value)


class MessageContext:
    def __init__(self, broker, app_id, message, bot=None):
        self.broker = broker
        self.app_id = app_id
        self.message = message
        if bot is None:
            bot = broker.get_bot(app_id)
        self.bot = bot
        self._cv_tokens = []

    def copy(self):
        return self.__class__(
            self.broker,
            self.app_id,
            self.message,
            bot=self.bot,
        )

    def push(self):
        broker_ctx = _cv_broker.get(None)
        if broker_ctx is None or broker_ctx.broker is not self.broker:
            broker_ctx = self.broker.broker_context()
            broker_ctx.push()
        else:
            broker_ctx = None
        self._cv_tokens.append((_cv_message.set(self), broker_ctx))

    def pop(self, exc=_sentinel):
        try:
            if len(self._cv_tokens) == 1:
                if exc is _sentinel:
                    exc = sys.exc_info()[1]
                # do_teardown_message_context(exc)
        finally:
            ctx = _cv_message.get()
            token, broker_ctx = self._cv_tokens.pop()
            _cv_message.reset(token)
            if broker_ctx is not None:
                broker_ctx.pop(exc)
            if ctx is not self:
                raise AssertionError(
                    f"Popped wrong message context. ({ctx!r} instead of {self!r})"
                )

    def __enter__(self):
        self.push()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.pop(exc_value)


class InstanceContext:
    def __init__(self):
        self._cv_tokens = []

    def push(self):
        from .broker import BaseBroker

        if _cv_broker.get(None) is None and isinstance(self, BaseBroker):
            _cv_broker.set(self.broker_context())
        self._cv_tokens.append(_cv_instance.set(self))

    def pop(self, exc=_sentinel):
        try:
            if len(self._cv_tokens) == 1:
                if exc is _sentinel:
                    exc = sys.exc_info()[1]
                # do_teardown_instance_context(exc)
        finally:
            instance = _cv_instance.get(None)
            from .broker import BaseBroker

            # can start broker ouside with
            if not isinstance(instance, BaseBroker):
                _cv_instance.reset(self._cv_tokens.pop())
            if instance is not self:
                raise AssertionError(
                    f"Popped wrong instance context. ({instance!r} instead of {self!r})"
                )

    def __enter__(self):
        self.push()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.pop(exc_value)
