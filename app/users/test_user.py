import pytest
from fastapi import status
from app.users.models import UserModel
from app.auth.jwt_auth import verify_access_token


def test_create_user(client, db_session):
    payload = {
        "email": "newuser@test.com",
        "full_name": "NewUser",
        "password": "newpassword",
        "password_confirm": "newpassword",
        "national_id": "9876543210",
        "gender": "female"
    }
    
    response = client.post("/api/v1/user", json=payload)
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == payload["email"]
    assert data["full_name"] == payload["full_name"]
    
   
    user_in_db = db_session.query(UserModel).filter_by(email=payload["email"]).first()
    assert user_in_db is not None
    assert user_in_db.full_name == payload["full_name"]



@pytest.mark.asyncio
async def test_user_login(async_client, async_db_session, auth_user):
    async_db_session.add(auth_user)
    await async_db_session.commit()

    login_payload = {
        "email": auth_user.email,
        "password": "hashed_password"
    }

    response = await async_client.post("/api/v1/login", json=login_payload)

    assert response.status_code == 202
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
