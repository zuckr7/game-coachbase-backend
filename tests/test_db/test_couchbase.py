# from app.db import db_users

# def test_create_get_delete_document():
#     # здесь можно мокать сам couchbase, но проверим логику:
#     key = "key1"
#     data = {"foo": "bar"}
#     assert db_users.create_document(key, data) is True

#     doc = db_users.get_document(key)
#     assert isinstance(doc, dict) and doc.get("foo") == "bar"

#     assert db_users.delete_document(key) is True
