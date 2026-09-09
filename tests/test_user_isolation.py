def test_user_isolation(client):
    # User A
    r = client.post("/auth/register", json={"email": "usera@example.com", "password": "pwA"})
    assert r.status_code == 200
    r2 = client.post("/auth/login", json={"email": "usera@example.com", "password": "pwA"})
    token_a = r2.json()["access_token"]

    # User B
    r = client.post("/auth/register", json={"email": "userb@example.com", "password": "pwB"})
    assert r.status_code == 200
    r2 = client.post("/auth/login", json={"email": "userb@example.com", "password": "pwB"})
    token_b = r2.json()["access_token"]

    # User A creates a warehouse
    headers_a = {"Authorization": f"Bearer {token_a}"}
    r = client.post("/warehouses/", json={"name": "A's WH"}, headers=headers_a)
    assert r.status_code == 201
    wh = r.json()
    wh_id = wh["id"]

    # User B tries to access A's warehouse -> 404
    headers_b = {"Authorization": f"Bearer {token_b}"}
    r = client.get(f"/warehouses/{wh_id}", headers=headers_b)
    assert r.status_code == 404

    # User A can access it
    r = client.get(f"/warehouses/{wh_id}", headers=headers_a)
    assert r.status_code == 200
