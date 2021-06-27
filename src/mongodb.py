from pymongo import MongoClient


class MongoDb:

    def __init__(self) -> None:

        mongo_db = 'swimlane'
        uri = 'mongodb://localhost:27017/db'
        client = MongoClient(uri)
        self.db = client[mongo_db]
