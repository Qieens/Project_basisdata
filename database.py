from pymongo import MongoClient
from config import Config

try:
    client = MongoClient(Config.MONGO_URI)

    db = client[Config.DATABASE_NAME]

    print("=" * 40)
    print("MongoDB Connected")
    print("Database :", Config.DATABASE_NAME)
    print("=" * 40)

except Exception as e:

    print("Gagal konek MongoDB")
    print(e)