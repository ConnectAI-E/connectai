import time
from .globals import current_broker
from .ctx import InstanceContext


class BaseBot(InstanceContext):

    def __init__(self, app_id='', app_secret=''):
        super().__init__()
        self.app_id = app_id
        self.app_secret = app_secret
        self.events = {}
        current_broker.register_bot(self)

    def on(self, event, fn):
        self.events[event] = fn

    def trigger(self, event, *args, **kwargs):
        if event in self.events:
            return self.events[event](*args, **kwargs)

    # def on(self, event, fn):
    #     if event not in self.events:
    #         self.events[event] = []
    #     self.events[event].append(fn)

    # def trigger(self, event, *args, **kwargs):
    #     result = None
    #     if event in self.events:
    #         for fn in self.events[event]:
    #             result = fn(*args, **kwargs)
    #     return result


class FeishuChatBot(BaseBot):

    def run(self, message):
        print('FeishuChatBot.run', message)
        time.sleep(1)
        print('FeishuChatBot.run', message)
        # return 'reply ' + message['content']
        return self.trigger('text', message)

    def send(self, message):
        print('FeishuChatBot.send', message)

    def send_text(self, fn=None):
        self.on('text', fn)



