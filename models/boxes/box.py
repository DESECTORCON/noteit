import datetime
import uuid
from config import ELASTIC_PORT as port
from elasticsearch import Elasticsearch
from common.database import Database
from models.boxes import constants as BoxConstants


class Box(object):

    def __init__(self, name='Demo Box', notes=[], created_date=datetime.datetime.now(), _id=None):
        self.name = name
        self.notes = notes
        self.created_date = created_date
        self._id = uuid.uuid4().hex if _id is None else _id

    def __repr__(self):
        return "<box {} with notes {} and created date {} ID: {}>".format(self.name,
                                                                          self.notes, self.created_date, self._id)

    def json(self):
        return {
            "_id": self._id,
            "name": self.name,
            "notes": self.notes,
            "created_date": self.created_date
        }

    def save_to_db(self):
        Database.insert(BoxConstants.COLLECTION, self.json())

    @classmethod
    def find_by_id(cls, box_id):
        return cls(**Database.find_one(BoxConstants.COLLECTION, {'_id': box_id}))

    def save_to_mongo(self):
        Database.update(BoxConstants.COLLECTION, {"_id": self._id}, self.json())

    def delete(self):
        Database.remove(BoxConstants.COLLECTION, {'_id': self._id})

    def delete_on_elastic(self):
        el = Elasticsearch(port=port)
        body = {
            "query": {
                "match": {
                    "box_id": self._id
                }
            }
        }
        el.delete_by_query(index="boxs", doc_type="box", body=body)
        del el
        return True

