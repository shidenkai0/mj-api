import uuid
import httpx
import pytest

from app.user.models import User
from tests.fixtures.core import generate_jwt_token

USER_EMAIL = "user@test.com"
USER_UID = uuid.uuid4()


@pytest.mark.asyncio
async def test_create_user(client: httpx.AsyncClient):
    jwt_token = generate_jwt_token(email=USER_EMAIL, user_id=str(USER_UID), is_email_verified=False)
    client.headers["Authorization"] = f"Bearer {jwt_token}"
    response = await client.post(
        "/users",
        json={
            "email": USER_EMAIL,
            "name": "Test",
            "language": "en",
        },
    )
    assert response.status_code == 200
    db_user = await User.get_by_supabase_uid(str(USER_UID))
    assert db_user is not None
    assert response.json() == {
        "id": str(db_user.id),
        "email": db_user.email,
        "supabase_uid": db_user.supabase_uid,
        "name": db_user.name,
    }


@pytest.mark.asyncio
async def test_create_user_already_exists(client: httpx.AsyncClient, test_user: User):
    jwt_token = generate_jwt_token(email=test_user.email, user_id=test_user.supabase_uid, is_email_verified=False)
    client.headers["Authorization"] = f"Bearer {jwt_token}"
    response = await client.post(
        "/users",
        json={
            "email": test_user.email,
            "name": "Test",
            "language": "en",
        },
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "User already registered"}


@pytest.mark.asyncio
async def test_create_user_invalid_token(client: httpx.AsyncClient):
    invalid_id_token = "invalid_id_token"
    client.headers["Authorization"] = f"Bearer {invalid_id_token}"
    response = await client.post(
        "/users",
        json={
            "email": "fake@email.com",
            "name": "Test",
            "language": "en",
        },
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_me(authenticated_client_user: httpx.AsyncClient, test_user: User):
    response = await authenticated_client_user.get("/users/me")
    assert response.status_code == 200
    assert response.json() == {
        "id": str(test_user.id),
        "email": test_user.email,
        "supabase_uid": test_user.supabase_uid,
        "name": test_user.name,
    }
