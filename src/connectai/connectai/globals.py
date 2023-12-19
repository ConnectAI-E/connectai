from contextvars import ContextVar

from werkzeug.local import LocalProxy

"""
1. broker_ctx: broker+event+sender
2. message_ctx: broker+bot
2. instance_ctx: current_instance 用于写多个层级的时候，不显式使用with也能找到对应的层级
"""


_no_broker_msg = "Working outside of broker context."
_cv_broker = ContextVar("connectai.broker_ctx")
broker_ctx = LocalProxy(_cv_broker, unbound_message=_no_broker_msg)
current_broker = LocalProxy(_cv_broker, "broker", unbound_message=_no_broker_msg)
broker = LocalProxy(_cv_broker, "broker", unbound_message=_no_broker_msg)
event = LocalProxy(_cv_broker, "event", unbound_message=_no_broker_msg)
sender = LocalProxy(_cv_broker, "sender", unbound_message=_no_broker_msg)


_no_message_msg = "Working outside of message context."
_cv_message = ContextVar("connectai.message_ctx")
message_ctx = LocalProxy(_cv_message, unbound_message=_no_message_msg)
bot = LocalProxy(_cv_message, "bot", unbound_message=_no_message_msg)
current_bot = LocalProxy(_cv_message, "bot", unbound_message=_no_message_msg)

_no_instance_msg = "Working outside of instance context."
_cv_instance = ContextVar("connectai.instance_ctx")
current_instance = LocalProxy(_cv_instance, unbound_message=_no_instance_msg)
