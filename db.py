import os
from couchbase.cluster import Cluster, ClusterOptions
from couchbase.auth import PasswordAuthenticator
from couchbase.exceptions import CouchbaseException
from dotenv import load_dotenv

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
            # Кластер
            self.cluster = Cluster(
                os.getenv('DB_HOST'),
                ClusterOptions(PasswordAuthenticator(
                    os.getenv('USERNAME'),
                    os.getenv('PASSWORD')
                ))
            )
            # Бакет
            self.bucket = self.cluster.bucket(os.getenv('BUCKET_NAME'))
            # Коллекция по умолчанию
            self.collection = self.bucket.default_collection()
            print("Успешное подключение к Couchbase!")
        except CouchbaseException as e:
            print(f"Ошибка подключения к Couchbase: {e}")

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

    def delete_document(self, key: str):
        # Удаление документа по ключу
        try:
            self.collection.remove(key)
            return True
        except CouchbaseException as e:
            print(f"Ошибка при удалении документа: {e}")
            return False

# Подключение к базе данных
db = CouchbaseDB()