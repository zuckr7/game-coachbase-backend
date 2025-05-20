import os, sys
import pytest
from fastapi.testclient import TestClient
from couchbase.exceptions import DocumentNotFoundException
    
os.environ.setdefault("ENV", "test")

from app.main import app
import app.db as _db

@pytest.fixture(scope="session")
def client():
    return TestClient(app)

@pytest.fixture
def auth_user_and_headers(client):
    # 1) создаём
    r = client.post("/users/", json={"username": "alice", "password": "secret"})
    assert r.status_code == 200, r.text
    user_id = r.json()["user_id"]

    # 2) логинимся
    r2 = client.post("/auth/login", data={"username": "alice", "password": "secret"})
    assert r2.status_code == 200, r2.text
    token = r2.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    return user_id, headers

@pytest.fixture(autouse=True)
def mock_password_hashing():
    from unittest.mock import patch
    with patch("app.auth_utils.hash_password", lambda pw: "fakehash"), \
         patch("app.auth_utils.verify_password", lambda pw, h: True):
        yield

@pytest.fixture(autouse=True)
def mock_couchbase_methods(monkeypatch):
    # простое in-memory хранилище для пользователей
    user_store = {}

    def fake_create_user(k, d):
        d = d.copy()
        d.setdefault("coins", 100) 
        d.setdefault("progress", {"passedLevel": 0, "points": 0, "coins": d["coins"], "items": []})
        user_store[k] = d
        return True

    def fake_get_user(k):
        return user_store.get(k)

    def fake_delete_user(k):
        return user_store.pop(k, None) is not None

    def fake_get_all_users():
        return list(user_store.values())

    def fake_get_by_name(username):
        return next((u.copy() for u in user_store.values() if u["username"] == username), None)

    monkeypatch.setattr(_db.db_users, "create_document", fake_create_user)
    monkeypatch.setattr(_db.db_users, "get_document", fake_get_user)
    monkeypatch.setattr(_db.db_users, "delete_document", fake_delete_user)
    monkeypatch.setattr(_db.db_users, "get_all_documents", fake_get_all_users)
    monkeypatch.setattr(_db.db_users, "get_user_by_username", fake_get_by_name)

    # чтобы _get_document работал тоже
    class DummyCol:
        def get(self, key):
            v = user_store.get(key)
            if v is None:
                raise DocumentNotFoundException()
            class R:
                def content_as(self, t): return v
            return R()
    monkeypatch.setattr(_db.db_users, "collection", DummyCol())


    level_store = {}

    def fake_create_lvl(k, d):
        level_store[k] = d.copy()
        return True

    def fake_get_lvl(k):
        return level_store.get(k)

    def fake_del_lvl(k):
        return level_store.pop(k, None) is not None

    def fake_get_all_lvls():
        return list(level_store.values())

    monkeypatch.setattr(_db.db_levels, "create_document", fake_create_lvl)
    monkeypatch.setattr(_db.db_levels, "get_document", fake_get_lvl)
    monkeypatch.setattr(_db.db_levels, "delete_document", fake_del_lvl)
    monkeypatch.setattr(_db.db_levels, "get_all_documents", fake_get_all_lvls)
    monkeypatch.setattr(_db.db_levels, "collection", DummyCol())

    yield

