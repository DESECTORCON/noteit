import datetime
import uuid


class Box(object):

    def __init__(self, name='Demo Box', notes=[], created_date=datetime.datetime.now(), _id=None):
        self.name = name
        self.notes = notes
        self.created_date = created_date
        self._id = uuid.uuid4().hex if _id is None else _id

    def __repr__(self):
        return

    def json(self):
        return
