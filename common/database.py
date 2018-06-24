import pymongo


class Database(object):
    URI = "mongodb://127.0.0.1:27017"
    DATABASE = None

    @staticmethod
    def initialize():
        client = pymongo.MongoClient(Database.URI)
        Database.DATABASE = client['Note_it_page']

    @staticmethod
    def insert(collection, data):
        Database.DATABASE[collection].insert(data)

    @staticmethod
    def find(collection, query):
        return Database.DATABASE[collection].find(query).sort('date', pymongo.DESCENDING)

    @staticmethod
    def find_one(collection, query):
        return Database.DATABASE[collection].find_one(query)

    @staticmethod
    def update(collection, query, data):
        Database.DATABASE[collection].update(query, data, upsert=True)

    @staticmethod
    def remove(collection, query):
        Database.DATABASE[collection].remove(query)

    @staticmethod
    def limit_find(collection, query, limit):
        return_value = Database.DATABASE[collection].find(query).limit(limit)
        return_value = return_value.sort('date', pymongo.DESCENDING)
        return_ = []
        for doc in return_value:
            return_.append(doc)
        return return_
