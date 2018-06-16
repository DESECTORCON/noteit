import datetime
import os
import uuid
from werkzeug.utils import secure_filename
from config import ELASTIC_PORT as port, ALLOWED_EXTENSIONS, UPLOAD_FOLDER
from elasticsearch import Elasticsearch
from common.database import Database
from models.group import constants as GroupConstants


class Group(object):
    def __init__(self, name, _id=None, members=[], description='', shared_notes=[]
                 , group_img_name='', shared="1", created_date=datetime.datetime.now()):
        self.name = name
        self._id = uuid.uuid4().hex if _id is None else _id
        self.members = members
        self.description = description
        self.shared_notes = shared_notes
        self.group_img_name = group_img_name
        self.shared = shared
        self.created_date = created_date

    def __repr__(self):
        return "<Group {} with members {}>".format(self.name, self.members)

    def json(self):
        return {
            "_id": self._id,
            "name": self.name,
            "members": self.members,
            "description": self.description,
            "shared_notes": self.shared_notes,
            "group_img_name": self.group_img_name,
            "shared": self.shared,
            "created_date": self.created_date
        }

    def save_to_db(self):
        Database.insert(GroupConstants.COLLECTION, self.json())

    @classmethod
    def find_by_id(cls, note_id):
        try:
            return cls(**Database.find_one(GroupConstants.COLLECTION, {'_id': note_id}))
        except TypeError:
            return None

    @classmethod
    def get_all_shared_groups(cls):
        return [cls(**elem) for elem in Database.find(GroupConstants.COLLECTION, {'shared': "1"})]

    def save_to_mongo(self):
        Database.update(GroupConstants.COLLECTION, {"_id": self._id}, self.json())

    def delete(self):
        Database.remove(GroupConstants.COLLECTION, {'_id': self._id})

    def delete_on_elastic(self):
        el = Elasticsearch(port=port)
        body = {
            "query": {
                "match": {
                    "group_id": self._id
                }
            }
        }
        el.delete_by_query(index="groups", doc_type="group", body=body)
        del el
        return True

    def save_to_elastic(self):
        el = Elasticsearch(port=port)
        doc = {
            "group_id": self._id,
            "name": self.name,
            "members": self.members,
            "description": self.description,
            "shared_notes": self.shared_notes,
            "shared":   self.shared
        }
        el.index(index="groups", doc_type='group', body=doc)
        del el
        return True

    def update_to_elastic(self):
        el = Elasticsearch(port=port)
        doc1 = {
            "query": {
                "match": {
                    'group_id': self._id
                }
            }
        }
        doc2 = {
            "group_id": self._id,
            "name": self.name,
            "members": self.members,
            "description": self.description,
            "shared_notes": self.shared_notes,
            "shared": self.shared
        }

        el.delete_by_query(index="groups", doc_type='group', body=doc1)
        el.index(index="groups", doc_type='group', body=doc2)
        del el
        return True

    @staticmethod
    def search_with_elastic(form_data, shared):
        el = Elasticsearch(port=port)

        if shared is True:
            shared = "1"
        else:
            shared = "0"

        if form_data is '':
            data = el.search(index='groups',body={
                "query": {
                    "bool": {
                        "must": [
                            {
                                "prefix": {"name": ""}
                            },
                            {
                                "match": {"shared": shared}
                            }
                        ]
                    }
                }
            })
        else:
            data = el.search(index='groups', body={
                "query": {
                    "bool": {
                        "must": [
                            {
                                "prefix": {"name": form_data}
                            },
                            {
                                "match": {"shared": shared}
                            }
                        ]
                    }
                }
            })

        notes = []
        for note in data['hits']['hits']:
            try:
                notes.append(Group.find_by_id(note['_source']['group_id']))
            except KeyError:
                notes.append(Group.find_by_id(note['_source']['query']['match']['group_id']))
        del el
        return notes

    @staticmethod
    def allowed_file(file):
        return '.' in file.filename and \
               file.filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    def save_img_file(self, file):
        if file and self.allowed_file(file.name):
            filename = secure_filename(file.name)
            file.save(os.path.join(UPLOAD_FOLDER, filename))

    def delete_img(self):
            try:
                for file in self.group_img_name:
                    os.remove(file)
            finally:
                return

