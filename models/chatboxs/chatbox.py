import datetime
import uuid
import shortid
from common.database import Database
from models.chatboxs.constants import COLLECTION as ChatBoxConstants
from models.messages.message import Message
from models.users.user import User


class ChatBox(object):

    def __init__(self, _id=None, user_ids=[], messages=[], created_date=datetime.datetime.now(), name=None, last_logined=None):
        self._id = uuid.uuid4().hex if _id is None else _id
        self.user_ids = user_ids
        self.messages = messages
        self.created_date = created_date
        self.last_logined = last_logined
        id_gen_sid = shortid.ShortId()
        self.name = id_gen_sid.generate() if name is None else name

    def json(self):
        return {
            "_id": self._id,
            "user_ids": self.user_ids,
            "messages": self.messages,
            "created_date": self.created_date,
            "last_logined": self.last_logined
        }

    def save_to_mongo(self):
        Database.update(ChatBoxConstants, {"_id": self._id}, self.json())

    @classmethod
    def find_by_id(cls, chatbox_id, limit=None):
        try:
            if limit is not None:
                return [cls(**elem) for elem in Database.limit_find(ChatBoxConstants, {'_id': chatbox_id}, limit=limit)]
            else:
                return [cls(**elem) for elem in Database.find_one(ChatBoxConstants, {'_id': chatbox_id})]
        except TypeError:
            return None

    def limit_find_messages(self):
        try:
            messages = []

            for message in self.messages:
                messages.append(Message.find_by_id(message))
            return messages

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

    def get_members(self):
        members = []
        for user in self.user_ids:
            members.append(User.find_by_id(user))

        return members

    def update_last_logined(self):
        self.last_logined = datetime.datetime.now()
        self.save_to_mongo()



