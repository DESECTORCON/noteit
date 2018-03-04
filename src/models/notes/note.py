import uuid
from src.common.database import Database
import src.models.notes.constants as NoteConstants
import datetime


class Note(object):

    def __init__(self, title, content, author_email, author_nickname, created_date=None, _id=None, shared=False,
                 share_only_with_users=False):
        self.title = "No title" if title is None else title
        self.content = "No content" if content is None else content
        self.created_date = datetime.datetime.now() if created_date is None else created_date
        self.author_email = author_email
        self._id = uuid.uuid4().hex if _id is None else _id
        self.shared = shared
        self.author_nickname = author_nickname
        self.share_only_with_users = share_only_with_users

    def __repr__(self):
        return "<Note {} with author {} and created date {}>".format(self.title, self.author_email, self.created_date)

    def json(self):
        return {
            "_id": self._id,
            "title": self.title,
            "content": self.content,
            "author_email": self.author_email,
            "created_date": self.created_date,
            "author_nickname": self.author_nickname,
            "shared": self.shared,
            "share_only_with_users": self.share_only_with_users
        }

    def save_to_db(self):
        Database.insert(NoteConstants.COLLECTION, self.json())

    @classmethod
    def find_by_user_email(cls, user_email):
        return [cls(**elem) for elem in Database.find(NoteConstants.COLLECTION, {'author_email': user_email})]

    @classmethod
    def find_by_id(cls, note_id):
        return cls(**Database.find_one(NoteConstants.COLLECTION, {'_id': note_id}))

    def save_to_mongo(self):
        Database.update(NoteConstants.COLLECTION, {"_id": self._id}, self.json())

    def delete(self):
        Database.remove(NoteConstants.COLLECTION, {'_id': self._id})

    def share_or_unshare(self):

        if self.shared == False:
            self.shared = True
        else:
            self.shared = False
        self.save_to_mongo()

    @classmethod
    def find_shared_notes(cls):
        return [cls(**elem) for elem in Database.find(NoteConstants.COLLECTION,
                                                      {"shared": True, "share_only_with_users": False})]

    @classmethod
    def find_shared_notes_by_user(cls, user_email):
        return [cls(**elem) for elem in Database.find(NoteConstants.COLLECTION,
                                                      {"shared": True, "author_email": user_email})]

    @classmethod
    def get_only_with_users(cls):
        return [cls(**elem) for elem in Database.find(NoteConstants.COLLECTION,
                                                      {"shared": False, "share_only_with_users": True})]

    @classmethod
    def get_all(cls):
        return [cls(**elem) for elem in Database.find(NoteConstants.COLLECTION,{})]
