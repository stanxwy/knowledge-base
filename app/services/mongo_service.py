from functools import lru_cache
import os
import logging
from typing import List, Dict, Any
from datetime import datetime
from pymongo import MongoClient, DESCENDING
from bson import ObjectId

logger = logging.getLogger(__name__)

class MongoDBClient:
    def __init__(self):
        try:
            self.mongo_url = os.getenv("MONGO_URL")
            self.db_name = os.getenv("MONGO_DB_NAME")
            self.client = MongoClient(self.mongo_url)
            self.db = self.client[self.db_name]
            self.chat_message = self.db["chat_message"]

            self.chat_message.create_index([("session_id", 1), ("ts", -1)])
            logger.info(f"Successfully connected to MongoDB: {self.db_name}")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise


class MongoService:
    def __init__(self):
        self._mongo_client = None

    def _get_mongo_client(self):
        if self._mongo_client is None:
            self._mongo_client = MongoDBClient()
        return self._mongo_client

    def clear_history(self, session_id: str) -> int:
        try:
            result = self._get_mongo_client().chat_message.delete_many({"session_id": session_id})
            logger.info(f"Deleted {result.deleted_count} messages for session {session_id}")
            return result.deleted_count
        except Exception as e:
            logger.error(f"Error clearing history for session {session_id}: {e}")
            return 0

    def save_chat_message(
        self,
        session_id: str,
        role: str,
        text: str,
        rewritten_query: str = "",
        item_names: List[str] = None,
        image_urls: List[str] = None,
        message_id: str = None
    ) -> str:

        ts = datetime.now().timestamp()
        document = {
            "session_id": session_id,
            "role": role,
            "text": text,
            "rewritten_query": rewritten_query or "",
            "item_names": item_names,
            "image_urls": image_urls,
            "ts": ts
        }

        mongo_client = self._get_mongo_client()
        if message_id:
            result = mongo_client.chat_message.update_one(
                {"_id": ObjectId(message_id)},
                {"$set": document}              
            )
            logger.info(f"Chat message updated: {document}")
            return message_id
        else:
            result = mongo_client.chat_message.insert_one(document)
            logger.info(f"Chat message inserted: {document}")
            return str(result.inserted_id)

    def update_message_item_names(self, ids: List[str], item_names: List[str]) -> int:
        try:
            result = self._get_mongo_client().chat_message.update_many(
                {
                    "_id": {"$in": [ObjectId(i) for i in ids]}
                },
                {"$set": {"item_names": item_names}}
            )
            logger.info(f"Updated {result.modified_count} records with item_names: {item_names}")
            return result.modified_count
        except Exception as e:
            logger.error(f"Error updating history item_names: {e}")
            return 0

    def get_recent_messages(self, session_id: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        try:
            query = {"session_id": session_id} if session_id else {}
            cursor = self._get_mongo_client().chat_message.find(query).sort("ts", DESCENDING).limit(limit)
            messages = list(cursor)
            for m in messages:
                logger.debug(f'{datetime.fromtimestamp(m["ts"]).strftime("%Y-%m-%d %H:%M:%S")} - {m["role"]}: {m["text"]}')
            return messages
        except Exception as e:
            logger.error(f"Error getting recent messages: {e}")
            return []

@lru_cache(maxsize=1)
def get_mongo_service() -> MongoService:
    return MongoService()