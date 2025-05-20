def test_create_and_get_user(client, auth_user_and_headers):
    user_id, headers = auth_user_and_headers

    r = client.get(f"/users/{user_id}", headers=headers)
    assert r.status_code == 200
    assert r.json()["user_id"] == user_id

def test_delete_user(client, auth_user_and_headers):
    user_id, headers = auth_user_and_headers

    r = client.delete(f"/users/{user_id}", headers=headers)
    assert r.status_code == 200

def test_delete_nonexistent_user(client, auth_user_and_headers):
    user_id, headers = auth_user_and_headers
    r = client.delete(f"/users/{user_id}", headers=headers)
    assert r.status_code == 200

    r2 = client.delete(f"/users/{user_id}", headers=headers)
    assert r2.status_code in (401, 404)

def test_create_user_with_missing_fields(client):
    r = client.post("/users/", json={"username": "user_without_password"})
    assert r.status_code == 422 

    r2 = client.post("/users/", json={"password": "somepass"})
    assert r2.status_code == 422 

def test_get_nonexistent_user(client, auth_user_and_headers):
    _, headers = auth_user_and_headers
    r = client.get("/users/nonexistent_id", headers=headers)
    assert r.status_code in (403, 404)

