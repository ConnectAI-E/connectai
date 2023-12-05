from .globals import current_broker
from .ctx import InstanceContext


class BaseBot(InstanceContext):

    def __init__(self, app_id='', app_secret=''):
        super().__init__()
        self.app_id = app_id
        self.app_secret = app_secret
        current_broker.register_bot(self)


class FeishuChatBot(BaseBot):
    pass




