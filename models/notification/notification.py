import datetime
import uuid
from common.database import Database
from models.notification.constants import COLLECTION as NotificationCollection


class Notification(object):

    def __init__(self, title, content, target=None, type='to_all_users', created_date=datetime.datetime.now()
                 , _id=None, dismis_to=[]):
        self._id = uuid.uuid4().hex if _id is None else _id
        self.title = title
        self.content = content
        self.target = target
        self.type = type
        if type not in ['to_all_users', 'to_group', 'to_user']:
            raise Exception("type invalid. Type has to be ['to_all_users', 'to_group', 'to_user']")
        self.created_date = created_date
        self.dismis_to = dismis_to

    def __repr__(self):
        return "<Notification {}, target: {}, type: {}>".format(self.title, self.target, self.type)

    def json(self):
        return {
            "_id": self._id,
            "title": self.title,
            "content": self.content,
            "target": self.target,
            "type": self.type,
            "created_date": self.created_date,
            "dismis_to": self.dismis_to
        }

    def save_to_db(self):
        Database.insert(NotificationCollection, self.json())

    @classmethod
    def find_by_id(cls, notification_id):
        return cls(**Database.find_one(NotificationCollection, {'_id': notification_id}))

    def save_to_mongo(self):
        Database.update(NotificationCollection, {"_id": self._id}, self.json())

    def delete(self):
        Database.remove(NotificationCollection, {'_id': self._id})

    def alert(self):
        return {'title': self.title, 'content': self.content, 'target': self.target, 'type': self.type}

    @classmethod
    def find_by_type(cls, type, target):
        try:
            return [cls(**Database.find_one(NotificationCollection, {'type': type, 'target': target}))]
        except TypeError:
            return None

    @classmethod
    def dismis_find(cls, type, target, session_id):
        try:
            finded_by_type = [cls(**Database.find_one(NotificationCollection, {'type': type, 'target': target}))]

            return_ = []
            for notifi in finded_by_type:
                if session_id not in notifi.dismis_to:
                    return_.append(notifi)

            return return_

        except TypeError:
            return None


