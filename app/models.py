from pymongo import MongoClient
from app.config import Config
import time

client = MongoClient(Config.MONGO_URI)
db = client['Trademarkia-Document-Retrieval']

class Document:
    collection = db.documents

    @staticmethod
    def insert(data):
        result = Document.collection.insert_one(data)
        return result.inserted_id

    @staticmethod
    def find(query):
        return Document.collection.find(query)

    @staticmethod
    def find_one(query):
        return Document.collection.find_one(query)

class User:
    collection = db.users

    @staticmethod
    def get_user(user_id):
        return User.collection.find_one({'_id': user_id})

    @staticmethod
    def create_user(user_id):
        return User.collection.insert_one({
            '_id': user_id,
            'request_count': 0,
            'last_reset': time.time()
        })

    @staticmethod
    def update_request_count(user_id):
        current_time = time.time()
        user = User.get_user(user_id)

        if user is None:
            # Create new user if not exists
            User.create_user(user_id)
            return {'request_count': 1}

        # Reset count if last reset was more than an hour ago
        if current_time - user['last_reset'] > 3600:
            update = {
                '$set': {
                    'request_count': 1,
                    'last_reset': current_time
                }
            }
        else:
            update = {
                '$inc': {'request_count': 1}
            }

        return User.collection.find_one_and_update(
            {'_id': user_id},
            update,
            return_document=True
        )