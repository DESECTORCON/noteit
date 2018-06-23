import datetime
import uuid
from common.database import Database
from models.chatboxs.constants import COLLECTION as ChatBoxConstants


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
        Database.insert(ChatBoxConstants, self.json())

    @classmethod
    def find_by_id(cls, chatbox_id):
        try:
            return cls(**Database.find_one(ChatBoxConstants.COLLECTION, {'_id': chatbox_id}))
        except TypeError:
            return None

    @classmethod
    def limit_find_by_id(cls, chatbox_id):
        try:
            return cls(**Database.limit_find(ChatBoxConstants.COLLECTION, {'_id': chatbox_id}, 20))
        except TypeError:
            return None

    def delete_member(self, member_id):
        # returns false when error accorded
        try:
            self.user_ids.remove(member_id)
        except ValueError:
            return False

    def add_member(self, user_id):
        # addes member by extending list
        self.user_ids.extend([user_id])

    def delete_message(self, message_id):
        """

        :param message_id: message's _id
        :return: returns false when error accorded
        """
        try:
            self.messages.remove(message_id)
        except ValueError:
            return False

    def add_message(self, message_id):
        self.messages.extend([message_id])



