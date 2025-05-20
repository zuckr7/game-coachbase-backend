def test_create_and_get_level(client):
    payload = {"name": "Level 1", "difficulty": "easy", "data": {}}
    r = client.post("/levels/", json=payload)
    assert r.status_code == 200
    level_id = r.json()["level_id"]

    r2 = client.get(f"/levels/{level_id}")
    assert r2.status_code == 200
    assert r2.json()["name"] == payload["name"]

def test_get_all_levels(client):
    r = client.get("/levels/")
    assert r.status_code == 200
    assert isinstance(r.json(), list)

def test_delete_level(client):
    payload = {"name": "TD", "difficulty": "easy", "data": {}}
    r = client.post("/levels/", json=payload)
    lid = r.json()["level_id"]
    r2 = client.delete(f"/levels/{lid}")
    assert r2.status_code == 200

def test_create_level_with_invalid_data(client):
    r = client.post("/levels/", json={"difficulty": "easy", "data": {}})
    assert r.status_code == 422

    r2 = client.post("/levels/", json={"name": "Level X", "difficulty": 123, "data": {}})
    assert r2.status_code == 422

def test_get_nonexistent_level(client):
    r = client.get("/levels/nonexistent_level_id")
    assert r.status_code == 404

def test_delete_nonexistent_level(client):
    r = client.delete("/levels/nonexistent_level_id")
    assert r.status_code == 404
