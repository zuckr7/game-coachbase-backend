import os
from couchbase.cluster import Cluster
from couchbase.options import ClusterOptions, ClusterTimeoutOptions
from couchbase.auth import PasswordAuthenticator
from couchbase.exceptions import CouchbaseException, DocumentNotFoundException
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
BUCKET_NAME = os.getenv("BUCKET_NAME")

if not all([DB_HOST, USERNAME, PASSWORD, BUCKET_NAME]):
    raise ValueError("Не удалось загрузить переменные из .env")

# CouchbaseDB
class CouchbaseDB:
    def __init__(self):
        self.cluster = None
        self.bucket = None
        self.collection = None
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
            self.bucket = self.cluster.bucket(os.getenv('BUCKET_NAME'))
            self.collection = self.bucket.default_collection()
            self.create_indexes()
            print("Успешное подключение к Couchbase!")
        except CouchbaseException as e:
            print(f"Ошибка подключения к Couchbase: {e}")

    def create_indexes(self):
        indexes = [
            {
                "name": "idx_username",
                "query": "CREATE INDEX `idx_username` ON `players_db`(`username`)"
            }
        ]

        for index in indexes:
            try:
                query = index["query"].format(bucket=self.bucket.name)
                self.cluster.query(query).execute()
            except CouchbaseException as e:
                if "already exists" not in str(e):
                    print(f"Ошибка создания индекса {index['name']}: {e}") 

    def check_index_exists(self):
        check_query = f"""
        SELECT * FROM system:indexes 
        WHERE name = 'idx_username' AND keyspace_id = '{self.bucket.name}'
        """
        result = self.cluster.query(check_query)
        return len(result.rows()) > 0

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
            print(f"Ошибка поиска пользователя: {e}")
            return None

# Подключение к базе данных
db = CouchbaseDB()