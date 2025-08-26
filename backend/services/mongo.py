from django.conf import settings
from pymongo import MongoClient
from functools import lru_cache
from urllib.parse import quote_plus


def _build_uri():
    if settings.MONGODB_URI:
        return settings.MONGODB_URI
    user = settings.MONGODB_USER
    password = settings.MONGODB_PASSWORD
    host = settings.MONGODB_HOST
    params = settings.MONGODB_PARAMS
    auth_source = getattr(settings, 'MONGODB_AUTH_SOURCE', '')
    if auth_source:
        # ensure authSource is present in query params
        if 'authSource=' not in params:
            params = (params + '&authSource=' + quote_plus(auth_source)) if params else ('authSource=' + quote_plus(auth_source))
    if user and password and host:
        return f"mongodb+srv://{quote_plus(user)}:{quote_plus(password)}@{host}/?{params}"
    # Fallback to localhost
    return "mongodb://localhost:27017"

@lru_cache(maxsize=1)
def get_client() -> MongoClient:
    return MongoClient(_build_uri())


def get_db():
    return get_client()[settings.MONGODB_DB_NAME]


def documents_collection():
    return get_db()[settings.MONGODB_COLLECTION_DOCUMENTS]


def chats_collection():
    return get_db()[settings.MONGODB_COLLECTION_CHATS]

def profiles_collection():
    return get_db()['profiles']
