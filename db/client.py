from pymongo import MongoClient
from keys.user import security

db_client = MongoClient(
    f"mongodb+srv://{security.db_user}:{security.db_password}@cluster0.1nicp3s.mongodb.net/?retryWrites=true&w=majority").IMDb

