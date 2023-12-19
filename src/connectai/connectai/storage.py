from .globals import current_broker


class BaseStorage(object):
    def __init__(self):
        current_broker.register_storage(self)

    def set(self, key, value):
        raise NotImplementedError

    def get(self, key):
        raise NotImplementedError

    def delete(self, key):
        pass

    def has(self, key):
        return True


class DictStorage(BaseStorage):
    def __init__(self):
        super().__init__()
        self.data = {}

    def set(self, key, value):
        self.data[key] = value

    def get(self, key):
        return self.data[key]

    def delete(self, key):
        del self.data[key]

    def has(self, key):
        return key in self.data

    def __repr__(self):
        return repr(self.data)
