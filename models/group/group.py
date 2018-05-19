import uuid


class Group(object):
    def __init__(self, name, _id=None, members=[], description=''):
        self.name = name
        self._id = uuid.uuid4().hex if _id is None else _id
