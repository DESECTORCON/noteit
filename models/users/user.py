import datetime
import uuid
from common.utils import Utils
from common.database import Database
import models.users.errors as UserErrors
import models.users.constants as UserConstants
from models.boxes.box import Box
from models.messages.message import Message
from models.notes.note import Note
from shortid import ShortId
from elasticsearch import Elasticsearch
from config import ELASTIC_PORT as port


class User(object):

    def __init__(self, email, password, _id=None, nick_name=None, last_logined=datetime.datetime.now(), friends=[]):
        self.email = email
        self.password = password
        self._id = uuid.uuid4().hex if _id is None else _id
        sid = ShortId()
        self.nick_name = "User " + sid.generate() if nick_name is None else nick_name
        self.last_logined = last_logined
        self.friends = friends

    def __repr__(self):
        return "<User {} with nick name {}>".format(self.email, self.nick_name)

    @staticmethod
    def is_login_valid(email, password):
        """
        This method verifies that an email/password combo (as sent by the site forms) is valid or not.
        Chacks that the e-mail exists, and that the password associated to that email is correct.
        :param email: The user's email
        :param password: A sha512 hashed password
        :return: True if valid, Flase otherwise
        """

        user_data = Database.find_one(UserConstants.COLLECTION, {"email": email})  # password in sha512 -> pbkdf2_sha512
        if user_data is None:

            raise UserErrors.UserNotExistsError("Your user does not exist. If you want to login, then register.")

        elif not Utils.check_hashed_password(password, user_data['password']):

            raise UserErrors.IncorrectPasswordError("Your password was wrong. Please try again.")

        return True

    @staticmethod
    def register_user(email, password, nick_name):
        el = Elasticsearch(port=port)
        """
        This method registers a user using e-mail and password
        The password already comes hashed as sha-512
        :param email: user's email (might be invalid)
        :param password: sha512-hashed password
        :return: True if registered successfully, of False otherwise (exceptions can also be raised)
        """
        user_data = Database.find_one(UserConstants.COLLECTION, {"email": email})

        if user_data is not None:
            # Tell user they are already registered
            raise UserErrors.UserAlreadyRegisteredError("The e-mail you used to register already exists.")

        if not Utils.email_is_valid(email):
            # Tell user that their e-mail is not constructed properly.
            raise UserErrors.InvalidEmailError("The e-mail does not have the right format.")

        if nick_name == '' or nick_name == None:

            User(email, Utils.hash_password(password), nick_name=None).save_to_mongo()
            doc = {
                'email': email,
                'nick_name': nick_name,
                'user_id': "",
            }

        else:
            User(email, Utils.hash_password(password), nick_name=nick_name).save_to_mongo()

            doc = {
                'email': email,
                'nick_name': nick_name,
                'user_id': "",
            }
        el.index(index="users", doc_type='user', body=doc, id=User.find_by_email(email)._id)

        return True

    def save_to_mongo(self):
        Database.update(UserConstants.COLLECTION, {"_id": self._id}, self.json())

    def json(self):
        return {
            "_id": self._id,
            "email": self.email,
            "password": self.password,
            "nick_name": self.nick_name,
            "last_logined": self.last_logined,
            "friends": self.friends
        }

    @classmethod
    def find_by_email(cls, email):
        return cls(**Database.find_one(UserConstants.COLLECTION, {'email': email}))

    def get_notes(self):
        return Note.find_by_user_email(self.email)

    @classmethod
    def get_all(cls):
        return [cls(**elem) for elem in Database.find(UserConstants.COLLECTION, {})]

    @classmethod
    def find_by_id(cls, id):
        return cls(**Database.find_one(UserConstants.COLLECTION, {'_id': id}))

    @classmethod
    def find_by_nickname_mulitple(cls, nickname):
        return [cls(**elem) for elem in Database.find(UserConstants.COLLECTION, {"nick_name": nickname})]

    def delete(self):
        el = Elasticsearch(port=port)
        el.delete_by_query(index='users', doc_type='user', body={'query': {'match': {"_id": self._id}}})

        Database.remove(UserConstants.COLLECTION, {'_id': self._id})

    def delete_user_notes(self):
        notes = Note.find_by_user_email(self.email)

        for note in notes:
            note.delete_on_elastic()
            note.delete_img()
            note.delete()

    def delete_user_messages(self):
        messages = Message.find_by_sender_id(self._id)

        for message in messages:
            message.delete_on_elastic()
            message.delete()

    def delete_user_boxes(self):
        boxes = Box.find_by_maker_id(self._id)

        for box in boxes:
            box.delete_on_elastic()
            box.delete()
