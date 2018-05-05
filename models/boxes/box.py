import datetime
import uuid
from config import ELASTIC_PORT as port
from elasticsearch import Elasticsearch
from common.database import Database
from models.boxes import constants as BoxConstants


class Box(object):

    def __init__(self, maker_id, name='Demo Box', notes=[], created_date=datetime.datetime.now(), _id=None):
        self.name = name
        self.notes = notes
        self.created_date = created_date
        self._id = uuid.uuid4().hex if _id is None else _id
        self.maker_id = maker_id

    def __repr__(self):
        return "<box {} with notes {} and created date {} ID: {}>".format(self.name,
                                                                          self.notes, self.created_date, self._id)

    def json(self):
        return {
            "_id": self._id,
            "name": self.name,
            "notes": self.notes,
            "created_date": self.created_date,
            "maker_id": self.maker_id
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

    @classmethod
    def get_user_boxes(cls, maker_id):
        return [cls(**elem) for elem in Database.find(BoxConstants.COLLECTION,
                                                      {"user_id": maker_id})]

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

    def save_to_elastic(self):
        el = Elasticsearch(port=port)
        doc = {
            'box_id': self._id,
            'name': self.name,
            'notes': self.notes,
            'created_date': self.created_date.strftime('%Y-%m-%d'),
            'maker_id': self.maker_id
        }
        el.index(index="boxs", doc_type='box', body=doc)
        del el
        return True

    def update_to_elastic(self):
        el = Elasticsearch(port=port)
        doc1 = {
            "query": {
                "match": {
                    'note_id': self._id
                }
            }
        }
        doc2 = {
            'box_id': self._id,
            'name': self.name,
            'notes': self.notes,
            'created_date': self.created_date.strftime('%Y-%m-%d'),
            'maker_id': self.maker_id
        }

        el.delete_by_query(index="boxs", doc_type='box', body=doc1)
        el.index(index="boxs", doc_type='box', body=doc2)
        del el
        return True

    @staticmethod
    def search_with_elastic(form_data, user_nickname=None):
        el = Elasticsearch(port=port)

        if form_data is '':
            data = el.search(index='boxs', doc_type='box', body={
                "query": {
                    "bool": {
                        "should": [
                            {
                                "prefix": {"title": ""},
                            },
                            {
                                "term": {"content": ""}
                            }
                        ],
                        "filter": [
                            {
                                "match": {"author_nickname": user_nickname}
                            }
                        ]
                    }
                }
            })
        else:
            data = el.search(index='boxs', doc_type='box', body={
                "query": {
                    "bool": {
                        "should": [
                            {
                                "prefix": {"title": form_data},
                            },
                            {
                                "term": {"content": form_data}
                            }
                        ],
                        "filter": [
                            {
                                "match": {"author_nickname": user_nickname}
                            }
                        ]
                    }
                }
            })

        notes = []
        for note in data['hits']['hits']:
            try:
                notes.append(Box.find_by_id(note['_source']['box_id']))
            except KeyError:
                notes.append(Box.find_by_id(note['_source']['query']['match']['box_id']))
        del el
        return notes

