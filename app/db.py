import os
from couchbase.cluster import Cluster
from couchbase.options import ClusterOptions
from couchbase.auth import PasswordAuthenticator
from couchbase.exceptions import CouchbaseException, DocumentNotFoundException
from typing import Optional
import datetime
from config import DB_HOST, USERNAME, PASSWORD, BUCKET_NAME, LEVELS_BUCKET


if not all([DB_HOST, USERNAME, PASSWORD, BUCKET_NAME]):
    raise ValueError("Не удалось загрузить переменные из .env")

# CouchbaseDB
class CouchbaseDB:
    def __init__(self, bucket_name: str, create_indexes: bool = True):
        self.bucket_name = bucket_name
        self.cluster = None
        self.bucket = None
        self.collection = None
        self.create_indexes_flag = create_indexes
        self.connect()

    def connect(self):
        try:
            # Подключение к кластеру
            self.cluster = Cluster(
                os.getenv('DB_HOST'),
                ClusterOptions(PasswordAuthenticator(
                    os.getenv('USERNAME'),
                    os.getenv('PASSWORD')
                ))
            )
            
            # Подключение к бакету и коллекции
            self.bucket = self.cluster.bucket(self.bucket_name)
            self.collection = self.bucket.default_collection()
            if self.create_indexes_flag:
                self.create_indexes()
            print(f"Успешное подключение к бакету: {self.bucket.name}")
        except CouchbaseException as e:
            print(f"Ошибка подключения к Couchbase: {e}")

    def create_indexes(self):
        indexes = [
            {
                "name": "idx_username",
                "query": f"CREATE INDEX `idx_username` ON `{self.bucket.name}`(`username`)"
            },
            {
                "name": "idx_vk_id",
                "query": f"CREATE INDEX `idx_vk_id` ON `{self.bucket.name}`(`vk_id`)"
            }
        ]

        for index in indexes:
            try:
                query = index["query"].format(bucket=self.bucket.name)
                self.cluster.query(query).execute()
            except CouchbaseException as e:
                if "already exists" not in str(e):
                    print(f"Ошибка создания индекса {index['name']}: {e}") 

    def create_document(self, key: str, data: dict):
        # Создание документа в Couchbase
        try:
            self.collection.upsert(key, data)
            return True
        except CouchbaseException as e:
            print(f"Ошибка при создании документа: {e}")
            return False

    def get_document(self, key: str):
        # Получение документа по ключу
        try:
            result = self.collection.get(key)
            return result.content_as[dict]
        except CouchbaseException as e:
            print(f"Ошибка при получении документа: {e}")
            return None
        
    def _get_document(self, key: str):
        # будет служебной для проверки существования id
        try:
            result = self.collection.get(key)
            return result.content_as[dict]
        except DocumentNotFoundException:
            return None
        except CouchbaseException as e:
            print(f"Ошибка при получении документа: {e}")
            return None

    def delete_document(self, key: str):
        # Удаление документа по ключу
        try:
            self.collection.remove(key)
            return True
        except CouchbaseException as e:
            print(f"Ошибка при удалении документа: {e}")
            return False
    
    def get_all_documents(self) -> list:
        query = f"SELECT META().id, * FROM `{self.bucket.name}`"
        try:
            result = self.cluster.query(query)
            rows = list(result.rows())
            documents = []
            for row in rows:
                doc = row[self.bucket.name]
                doc["id"] = row["id"]
                documents.append(doc)
            return documents
        except Exception as e:
            print(f"Ошибка получения документов: {e}")
            return []
        
    def get_user_by_username(self, username: str) -> Optional[dict]:
        query = f"""
        SELECT META().id, * FROM `{self.bucket.name}` 
        WHERE username = $username 
        LIMIT 1
        """
        try:
            result = self.cluster.query(query, username=username)
            
            rows = list(result.rows())

            if not rows:
                return None
            row = rows[0]
            return {
                "user_id": row['id'],
                **row[self.bucket.name]
            }
            
        except CouchbaseException as e:
            print(f"Ошибка поиска пользователя по username: {e}")
            return None
    
    def get_user_by_vk_id(self, vk_id: str) -> Optional[dict]:
        query = f"""
        SELECT META().id, * FROM `{self.bucket.name}` 
        WHERE vk_id = $vk_id 
        LIMIT 1
        """
        try:
            result = self.cluster.query(query, vk_id=vk_id)
            rows = list(result.rows())
            if not rows:
                return None
            row = rows[0]
            return {
                "user_id": row['id'],
                **row[self.bucket.name]
            }
        except CouchbaseException as e:
            print(f"Ошибка поиска пользователя по vk_id: {e}")
            return None
        
    def get_leaderboard(self, limit: int = 10):
        query = f"""
        SELECT META().id as user_id,
            username,
            created_at,
            version
        FROM `{self.bucket.name}`
        WHERE progress.points IS NOT MISSING
        ORDER BY progress.points DESC
        LIMIT {limit}
        """
        try:
            result = self.cluster.query(query)
            return [row for row in result.rows()]
        except Exception as e:
            print(f"Ошибка получения leaderboard: {e}")
            return None

# Подключение к базе данных
db_users = CouchbaseDB(BUCKET_NAME, create_indexes=True)      # для пользователей
db_levels = CouchbaseDB(LEVELS_BUCKET, create_indexes=False)     # для уровней

