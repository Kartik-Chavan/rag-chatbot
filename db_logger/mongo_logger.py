from pymongo import MongoClient
from datetime import datetime
from config.settings import (
    MONGODB_URI,
    MONGODB_DB_NAME,
    MONGODB_CERT_PATH,
    LOG_COLLECTION_CHAT,
    LOG_COLLECTION_POLICY,
    LOG_COLLECTION_ERROR,
)


class MongoLogger:
    def __init__(self):
        try:
            # Disable logging if config is incomplete
            if not MONGODB_URI or not MONGODB_CERT_PATH:
                self.client = None
                self.db = None
                return

            self.client = MongoClient(
    MONGODB_URI,
    tls=True,
    tlsCertificateKeyFile=MONGODB_CERT_PATH,
    serverSelectionTimeoutMS=2000
)

            # Optional: force early connection check
            self.client.admin.command("ping")

            self.db = self.client[MONGODB_DB_NAME]

        except Exception as e:
            print(f"[MongoLogger] Connection failed: {e}")
            self.client = None
            self.db = None

    def _safe_insert(self, collection_name: str, data: dict):
        if self.db is None:
            print("[MongoLogger] Logging is disabled due to missing configuration.")
            return  # logging safely disabled

        try:
            data["timestamp"] = datetime.utcnow()
            self.db[collection_name].insert_one(data)
            print(f"[MongoLogger] Logged to {collection_name}")
        except Exception as e:
            # Never crash the app because of logging
            print(f"[MongoLogger] Failed to log to {collection_name}: {e}")

    def log_chat(self, data: dict):
        self._safe_insert(LOG_COLLECTION_CHAT, data)

    def log_policy(self, data: dict):
        self._safe_insert(LOG_COLLECTION_POLICY, data)

    def log_error(self, data: dict):
        self._safe_insert(LOG_COLLECTION_ERROR, data)
