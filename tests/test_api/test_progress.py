def test_update_and_get_progress(client, auth_user_and_headers):
    user_id, headers = auth_user_and_headers

    progress = {"passedLevel": 2, "points": 50, "coins": 10, "items": [{"name": "sword"}]}
    r1 = client.patch(f"/users/{user_id}/progress", headers=headers, json=progress)
    assert r1.status_code == 200

    r2 = client.get(f"/users/{user_id}/progress", headers=headers)
    assert r2.status_code == 200
    assert r2.json()["points"] == 50

def test_update_progress_with_invalid_data(client, auth_user_and_headers):
    user_id, headers = auth_user_and_headers

    r = client.patch(f"/users/{user_id}/progress", headers=headers, json={"points": "a lot"})
    assert r.status_code == 422

def test_get_progress_nonexistent_user(client, auth_user_and_headers):
    _, headers = auth_user_and_headers
    r = client.get("/users/nonexistent_id/progress", headers=headers)
    assert r.status_code in (403, 404)
