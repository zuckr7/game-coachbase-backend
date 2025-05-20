def test_login(client):
    client.post("/users/", json={"username": "loginuser", "password": "pass"})
    resp = client.post("/auth/login", data={"username": "loginuser", "password": "pass"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()
