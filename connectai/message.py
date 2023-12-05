from typing import Dict


class Message(Dict):

    def __getattr__(self, name):
        return self[name]

