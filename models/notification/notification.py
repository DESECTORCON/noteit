import datetime
import uuid
from common.database import Database
from models.notification.constants import COLLECTION as NotificationCollection


class Notification(object):

    def __init__(self, _id, title, content, target=None, type='to_all_users', created_date=datetime.datetime.now()):
        self._id = uuid.uuid4().hex if _id is None else _id
        self.title = title
        self.content = content
        self.target = target
        self.type = type
        if type not in ['to_all_users', 'to_group', 'to_user']:
            raise Exception("type invalid. Type has to be ['to_all_users', 'to_group', 'to_user']")
        self.created_date = created_date

    def __repr__(self):
        return "<Notification {}, target: {}, type: {}>".format(self.title, self.target, self.type)

    def json(self):
        return {
            "_id": self._id,
            "title": self.title,
            "content": self.content,
            "target": self.target,
            "type": self.type,
            "created_date": self.created_date
        }

    def save_to_db(self):
        Database.insert(NotificationCollection.COLLECTION, self.json())

    @classmethod
    def find_by_id(cls, notification_id):
        return cls(**Database.find_one(NotificationCollection.COLLECTION, {'_id': notification_id}))

    def save_to_mongo(self):
        Database.update(NotificationCollection.COLLECTION, {"_id": self._id}, self.json())

    def delete(self):
        Database.remove(NotificationCollection.COLLECTION, {'_id': self._id})

    def alert(self):
        return {'title': self.title, 'content': self.content, 'target': self.target, 'type': self.type}

