import datetime
import uuid
from common.database import Database


class ChatBox(object):

    def __init__(self, _id, user_ids=[], messages=[], created_date=datetime.datetime.now()):
        self._id = uuid.uuid4().hex if _id is None else _id
        self.user_ids = user_ids
        self.messages = messages
        self.created_date = created_date
        self.max_exists_time = datetime.timedelta(days=100)

    def json(self):
        return {
            "_id": self._id,
            "user_ids": self.user_ids,
            "messages": self.messages,
            "created_date": self.created_date,
            "max_exists_time": self.max_exists_time
        }

    def save_to_mongo(self):
        Database.insert(ErrorLogConstants.COLLECTION, self.json())
