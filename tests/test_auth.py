def test_register_and_login(client):
    # Register
    r = client.post("/auth/register", json={"email": "a@example.com", "password": "secret"})
    assert r.status_code == 200
    data = r.json()
    assert data["email"] == "a@example.com"

    # Duplicate register should fail with 409
    r2 = client.post("/auth/register", json={"email": "a@example.com", "password": "secret"})
    assert r2.status_code == 409

    # Login
    r3 = client.post("/auth/login", json={"email": "a@example.com", "password": "secret"})
    assert r3.status_code == 200
    tok = r3.json()
    assert "access_token" in tok

    # Invalid login
    r4 = client.post("/auth/login", json={"email": "a@example.com", "password": "wrong"})
    assert r4.status_code == 401
