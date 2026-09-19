import os
from datetime import datetime, timezone
from dotenv import load_dotenv
from pymongo import ASCENDING, DESCENDING, MongoClient
from pymongo.errors import PyMongoError

load_dotenv()
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "vyaparvoice")
_client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=3000, connect=False)
db = _client[MONGODB_DATABASE]
owners = db.store_owners
products = db.products
transactions = db.transactions
assistant_logs = db.assistant_logs


def utc_now():
    return datetime.now(timezone.utc)


def ensure_indexes():
    owners.create_index([("email", ASCENDING)], unique=True)
    products.create_index([("owner_id", ASCENDING)])
    products.create_index([("owner_id", ASCENDING), ("name", ASCENDING)])
    transactions.create_index([("owner_id", ASCENDING)])
    transactions.create_index([("owner_id", ASCENDING), ("created_at", DESCENDING)])
    assistant_logs.create_index([("owner_id", ASCENDING)])


def ping_database():
    _client.admin.command("ping")


def database_status():
    try:
        ping_database()
        return "connected"
    except PyMongoError:
        return "disconnected"
