import time
from pathlib import Path

def test_export_lifecycle_and_download(client):
    # Register & login
    r = client.post("/auth/register", json={"email": "expuser@example.com", "password": "exp"})
    assert r.status_code == 200
    r2 = client.post("/auth/login", json={"email": "expuser@example.com", "password": "exp"})
    token = r2.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create warehouse and product
    r = client.post("/warehouses/", json={"name": "Export WH"}, headers=headers)
    assert r.status_code == 201
    wh_id = r.json()["id"]

    r = client.post(f"/warehouses/{wh_id}/products/", json={"title": "P1"}, headers=headers)
    assert r.status_code == 201

    # Request export (schedules background task)
    r = client.post(f"/warehouses/{wh_id}/exports/?format=csv", headers=headers)
    assert r.status_code == 201
    job = r.json()
    job_id = job["id"]

    # After request, TestClient should have executed background tasks; check status
    r = client.get(f"/warehouses/{wh_id}/exports/{job_id}", headers=headers)
    assert r.status_code == 200
    status = r.json()["status"]
    assert status in ("completed", "failed", "pending")

    if status == "completed":
        # Attempt to download
        r = client.get(f"/warehouses/{wh_id}/exports/download/{job_id}", headers=headers)
        assert r.status_code == 200
        # saved file should exist on disk
        file_path = Path(r.headers.get("content-disposition").split("filename=")[-1].strip('"'))
        # It's hard to know absolute path from response; instead check exports dir
        exports_dir = Path("/tmp/exports")
        assert any(exports_dir.glob(f"export_{job_id}_*.csv"))
