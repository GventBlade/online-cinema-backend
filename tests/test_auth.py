import pytest
from fastapi import status
from app.models import User

def test_register_user_success(client):
    payload = {
        "email": "test_user_2026@example.com",
        "password": "Strongpassword1231!"
    }

    response = client.post("/api/v1/auth/register", json=payload)
    print("\nМій JSON відповіді від FastAPI:", response.json())
    assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_200_OK]

    data = response.json()
    assert data["email"] == payload["email"]
    assert "id" in data


def test_register_user_already_exists(client):
    payload = {
        "email": "duplicate@example.com",
        "password": "Password125!"
    }

    client.post("/api/v1/auth/register", json=payload)

    response = client.post("/api/v1/auth/register", json=payload)

    assert response.status_code == status.HTTP_409_CONFLICT


def test_login_user_success(client, db_session):

    email = "login_test@example.com"
    password = "SecurePassword123!"

    register_payload = {
        "email": email,
        "password": password
    }
    client.post("/api/v1/auth/register", json=register_payload)

    user = db_session.query(User).filter(User.email == email).first()
    if user:
        user.is_active = True
        db_session.commit()

    login_payload = {
        "username": email,
        "password": password
    }
    response = client.post("/api/v1/auth/login", data=login_payload)

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_get_protected_route_without_token(client):

    response = client.get("/api/v1/payments/my")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_protected_route_with_invalid_token(client):
    headers = {
        "Authorization": "Bearer totalmente_fake_token_123"
    }

    response = client.get("/api/v1/payments/my", headers=headers)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED