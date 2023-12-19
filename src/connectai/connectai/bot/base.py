import time

from flask import Request

from ..ctx import InstanceContext
from ..globals import current_broker
from ..message import Message


class BaseBot(InstanceContext):
    def __init__(self, app_id=""):
        super().__init__()
        self.app_id = app_id
        self.events = {}
        current_broker.register_bot(self)

    def parse_message(self, content):
        return Message(app_id=self.app_id, content=content)

    def filter(self, message):
        # 支持使用事件按顺序进行过滤，遇到失败的就返回False
        for fn in self.events.get("filter", []):
            if not fn(message):
                return False
        return True

    # def on(self, event, fn):
    #     self.events[event] = fn

    # def trigger(self, event, *args, **kwargs):
    #     if event in self.events:
    #         return self.events[event](*args, **kwargs)

    def get_message_id(self, message):
        raise NotImplementedError

    def on(self, event, fn):
        if event not in self.events:
            self.events[event] = []
        self.events[event].append(fn)

    def trigger(self, event, *args, **kwargs):
        events = self.events.get(event, [])
        if len(events) == 0:
            return
        # 单个事件支持多回调函数
        # 这里返回结果的时候，如果只有一个结果，就不返回数组，有多个结果就返回数组
        result = [fn(*args, **kwargs) for fn in events]
        return result[0] if len(result) == 1 else result
