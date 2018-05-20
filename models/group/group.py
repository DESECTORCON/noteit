import uuid


class Group(object):
    def __init__(self, name, _id=None, members=[], description='', shared_notes=[]):
        self.name = name
        self._id = uuid.uuid4().hex if _id is None else _id
        self.members = members
        self.description = description
        self.shared_notes = shared_notes

    def __repr__(self):
        return "<Group {} with members {}>".format(self.name, self.members)


