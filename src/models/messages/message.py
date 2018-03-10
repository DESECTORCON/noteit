import uuid
from src.common.database import Database
import src.models.messages.constants as MessageConstants
import datetime


class Message(object):

    def __init__(self, title, content, reciver_id, sender_id, sended_date=None, readed_date=None ,_id=None, readed_by_reciver=False, is_a_noteOBJ=False):
        self._id = uuid.uuid4().hex if _id is None else _id
        self.title = title
        self.content = content
        self.reciver_id = reciver_id
        self.sender_id = sender_id
        self.readed_date = readed_date
        self.sended_date = datetime.datetime.now() if sended_date is None else sended_date
        self.readed_by_reciver = readed_by_reciver
        self.is_a_noteOBJ = is_a_noteOBJ

    def __repr__(self):
        return "<Message title:{} with sender {} and reciver {}>".format(self.title, self.sender_id, self.reciver_id)

    def json(self):
        return {
            "title": self.title,
            "content": self.content,
            "reciver_id": self.reciver_id,
            "sender_id": self.sender_id,
            "readed_date": self.readed_date,
            "sended_date": self.sended_date,
            "readed_by_reciver": self.readed_by_reciver,
            "is_a_noteOBJ": self.is_a_noteOBJ
        }

    def save_to_db(self):
        Database.insert(MessageConstants.COLLECTION, self.json())

    def save_to_mongo(self):
        Database.update(MessageConstants.COLLECTION, {"_id": self._id}, self.json())

    @classmethod
    def find_by_sender_id(cls, sender_id):
        return [cls(**elem) for elem in Database.find(MessageConstants.COLLECTION, {'sender_id': sender_id})]

    @classmethod
    def find_by_reciver_id(cls, reciver_id):
        return [cls(**elem) for elem in Database.find(MessageConstants.COLLECTION, {'reciver_id': reciver_id})]

    @classmethod
    def find_by_id(cls, message_id):
        try:
            return cls(**Database.find_one(MessageConstants.COLLECTION, {"_id": message_id}))
        except TypeError:
            return None

    @classmethod
    def find_all(cls):
        return [cls(**elem) for elem in Database.find(MessageConstants.COLLECTION, {})]

    def delete(self):
        Database.remove(MessageConstants.COLLECTION, {"_id": self._id})

    def find_recivers_in_message_obj(self, message_id):
        message = self.find_by_id(message_id)
        recivers = message.reciver_id
        return recivers
