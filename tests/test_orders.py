from starlette.testclient import TestClient

from poshub_api.main import app


# Synchronous tests (for regular endpoints)
def test_create_order_sync():
    client = TestClient(app)

    # Test successful creation (201)
    response = client.post(
        "/orders",
        json={"customer_name": "Test", "total_amount": 100, "currency": "USD"},
        headers={
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzbWNwLXVzZXIiLCJzY29wZXMiOlsib3JkZXJzOndyaXRlIl19.rSn3mhqkfEQoZo5v4VdIEZTIWaeKan3oog4P-Th5TAI"
        },  # Mock or use test token
    )
    assert response.status_code == 201
    assert "order" in response.json()

    # Test validation error (422)
    response = client.post(
        "/orders",
        json={"invalid": "data"},
        headers={
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzbWNwLXVzZXIiLCJzY29wZXMiOlsib3JkZXJzOndyaXRlIl19.rSn3mhqkfEQoZo5v4VdIEZTIWaeKan3oog4P-Th5TAI"
        },
    )
    assert response.status_code == 422
