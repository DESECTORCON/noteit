import uuid
from common.database import Database
import models.messages.constants as MessageConstants
import datetime
from elasticsearch import Elasticsearch
from config import ELASTIC_PORT as port
from collections import OrderedDict


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
            "is_a_noteOBJ": self.is_a_noteOBJ,
            "_id": self._id
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

    @classmethod
    def find_by_recivers_not_readed(cls, reciver_id):
        return [cls(**elem) for elem in Database.find(MessageConstants.COLLECTION,
                                                      {'reciver_id': reciver_id, "readed_by_reciver":False})]

    @classmethod
    def find_by_viewers_id(cls, viewer_id):
        return [cls(**elem) for elem in Database.find(MessageConstants.COLLECTION, {"reciver_id": [viewer_id]})]

    def save_to_elastic(self):
        el = Elasticsearch(port=port)
        doc = {
            "title": self.title,
            "content": self.content,
            "reciver_id": self.reciver_id,
            "sender_id": self.sender_id,
            "sended_date": self.sended_date.strftime('%Y-%m-%d'),
            "readed_by_reciver": self.readed_by_reciver,
            "is_a_noteOBJ": self.is_a_noteOBJ,
            "message_id": self._id
        }
        el.index(index="messages", doc_type='message', body=doc)
        del el
        return True

    def update_to_elastic(self):
        el = Elasticsearch(port=port)
        doc1 = {
            "query": {
                "match": {
                    "message_id": self._id
                }
            }
        }
        doc2 = {
            "title": self.title,
            "content": self.content,
            "reciver_id": self.reciver_id,
            "sender_id": self.sender_id,
            "sended_date": self.sended_date.strftime('%Y-%m-%d'),
            "readed_by_reciver": self.readed_by_reciver,
            "is_a_noteOBJ": self.is_a_noteOBJ,
            "message_id": self._id
        }

        el.delete_by_query(index="messages", doc_type='message', body=doc1)
        el.index(index="messages", doc_type='message', body=doc2)
        del el
        return True

    def delete_on_elastic(self):
        el = Elasticsearch(port=port)
        body = {
            "query": {
                "match": {
                    "message_id": self._id
                }
            }
        }
        el.delete_by_query(index="messages", doc_type='message', body=body)
        del el
        return True

    @staticmethod
    def search_on_elastic(form, user_id):

        el = Elasticsearch(port=port)

        if form is '':
            data = el.search(index='messages', doc_type='message', body={
                "query": {
                    "bool": {
                        "should": [
                            {
                                "prefix": {"title": ""}
                            },
                            {
                                "term": {"content": ""}
                            }
                        ],
                        "filter": [
                            {
                                "match": {"reciver_id": user_id}
                            }
                        ]
                    }
                }
            })
        else:
            data = el.search(index='messages', doc_type='message', body={
                "query": {
                    "bool": {
                        "should": [
                            {
                                "prefix": {"title": form},
                            },
                            {
                                "term": {"content": form}
                            }
                        ],
                        "filter": [
                            {
                                "match": {"reciver_id": user_id}
                            }
                        ]
                    }
                }
            })

        messages = []
        for message in data['hits']['hits']:
            try:
                messages.append(Message.find_by_id(message['_source']['message_id']))
            except KeyError:
                messages.append(Message.find_by_id(message['_source']['query']['match']['message_id']))

        return messages

    @staticmethod
    def search_find_all(form, user_id):
        el = Elasticsearch(port=port)

        if form is '':
            body1 = {
  "query": {
    "bool": {
      "should": [
        {"prefix": {"title": ""}},
        {"term": {"content": ""}}
      ],

      "filter": {
        "bool": {
          "should": [
            {"match": {"reciver_id": user_id}},
            {"match": {"sender_id": user_id}}
          ]
        }
      }
    }
  }
}

            data1 = el.search(index='messages', doc_type='message', body=body1)

        else:
            body1 = {
  "query": {
    "bool": {
      "should": [
        {"prefix": {"title": form}},
        {"term": {"content": form}}
      ],

      "filter": {
        "bool": {
          "should": [
            {"match": {"reciver_id": user_id}},
            {"match": {"sender_id": user_id}}
          ]
        }
      }
    }
  }
}

            data1 = el.search(index='messages', doc_type='message', body=body1)

        messages = []
        for message in data1['hits']['hits']:
            try:
                messages.append(Message.find_by_id(message['_source']['message_id']))
            except KeyError:
                messages.append(Message.find_by_id(message['_source']['query']['match']['message_id']))

        return messages


