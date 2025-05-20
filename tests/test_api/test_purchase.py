def test_purchase_item(client, auth_user_and_headers):
    user_id, headers = auth_user_and_headers

    purchase = {"name": "apple", "quantity": 1, "price": 10}
    r = client.post(f"/users/{user_id}/purchase", headers=headers, json=purchase)
    assert r.status_code == 200
    assert "coins" in r.json()

def test_purchase_with_sufficient_coins(client, auth_user_and_headers):
    user_id, headers = auth_user_and_headers

    purchase = {"name": "apple", "quantity": 1, "price": 50}  
    r = client.post(f"/users/{user_id}/purchase", headers=headers, json=purchase)
    assert r.status_code == 200
    assert r.json()["coins"] == 50  # 100 - 50

def test_purchase_with_insufficient_coins(client, auth_user_and_headers):
    user_id, headers = auth_user_and_headers

    purchase = {"name": "apple", "quantity": 3, "price": 50}  # 150 > 100
    r = client.post(f"/users/{user_id}/purchase", headers=headers, json=purchase)
    assert r.status_code == 400
    assert "Insufficient coins" in r.text

def test_purchase_updates_inventory(client, auth_user_and_headers):
    user_id, headers = auth_user_and_headers

    purchase = {"name": "sword", "quantity": 1, "price": 30}
    r = client.post(f"/users/{user_id}/purchase", headers=headers, json=purchase)
    assert r.status_code == 200

    r2 = client.get(f"/users/{user_id}/progress", headers=headers)
    assert r2.status_code == 200
    items = r2.json().get("items", [])
    assert any(item["name"] == "sword" for item in items)

def test_purchase_invalid_data(client, auth_user_and_headers):
    user_id, headers = auth_user_and_headers

    purchase = {"name": "apple", "quantity": -1, "price": 10}
    r = client.post(f"/users/{user_id}/purchase", headers=headers, json=purchase)
    assert r.status_code == 422 

    purchase = {"quantity": 1, "price": 10}
    r = client.post(f"/users/{user_id}/purchase", headers=headers, json=purchase)
    assert r.status_code == 422

def test_purchase_multiple_items(client, auth_user_and_headers):
    user_id, headers = auth_user_and_headers

    purchases = [
        {"name": "shield", "quantity": 1, "price": 20},
        {"name": "potion", "quantity": 2, "price": 5},
    ]
    for purchase in purchases:
        r = client.post(f"/users/{user_id}/purchase", headers=headers, json=purchase)
        assert r.status_code == 200

    r2 = client.get(f"/users/{user_id}/progress", headers=headers)
    items = r2.json().get("items", [])
    names = [item["name"] for item in items]
    assert "shield" in names
    assert "potion" in names

def test_purchase_with_zero_quantity(client, auth_user_and_headers):
    user_id, headers = auth_user_and_headers

    purchase = {"name": "apple", "quantity": 0, "price": 10}
    r = client.post(f"/users/{user_id}/purchase", headers=headers, json=purchase)
    assert r.status_code == 422

def test_purchase_nonexistent_user(client, auth_user_and_headers):
    _, headers = auth_user_and_headers
    purchase = {"name": "apple", "quantity": 1, "price": 10}
    r = client.post("/users/nonexistent_user/purchase", headers=headers, json=purchase)
    assert r.status_code in (403, 404)
