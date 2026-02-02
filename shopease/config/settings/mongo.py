from pymongo import MongoClient
from decouple import config

client = MongoClient(config("MONGO_URI"))
mongo_db = client[config("MONGO_DB_NAME")]
