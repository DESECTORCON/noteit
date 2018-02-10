import datetime
import uuid
from src.common.utils import Utils
from src.common.database import Database
import src.models.users.errors as UserErrors
import src.models.users.constants as UserConstants
from src.models.notes.note import Note
from shortid import ShortId


class User(object):
    __searchable__ = ['email', 'nick_name', '_id']

    def __init__(self, email, password, _id=None, nick_name=None, last_logined=datetime.datetime.now()):
        self.email = email
        self.password = password
        self._id = uuid.uuid4().hex if _id is None else _id
        sid = ShortId()
        self.nick_name = "User " + sid.generate() if nick_name is None else nick_name
        self.last_logined = last_logined

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

        else:
            User(email, Utils.hash_password(password), nick_name=nick_name).save_to_mongo()

        return True

    def save_to_mongo(self):
        Database.update(UserConstants.COLLECTION, {"_id": self._id}, self.json())

    def json(self):
        return {
            "_id": self._id,
            "email": self.email,
            "password": self.password,
            "nick_name": self.nick_name,
            "last_logined": self.last_logined
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
        Database.remove(UserConstants.COLLECTION, {'_id': self._id})

    def delete_user_notes(self):
        notes = self.find_by_nickname_mulitple(self.nick_name)

        for note in notes:
            note.delete()
