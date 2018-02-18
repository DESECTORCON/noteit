import uuid
from src.common.database import Database
import src.models.error_logs.constants as ErrorLogConstants
import datetime


class Error_(object):

    def __init__(self, error_msg, error_date=datetime.datetime.now(), error_location=None, _id=None):
        self.error_msg = error_msg
        self.error_date = error_date
        self.error_location = error_location
        self._id = uuid.uuid4().hex if _id is None else _id

    def json(self):
        return {
            "error_msg": self.error_msg,
            "error_date": self.error_date,
            "error_location": self.error_location,
            "_id": self._id,
        }

    def save_to_mongo(self):
        Database.insert(ErrorLogConstants.COLLECTION, self.json())
