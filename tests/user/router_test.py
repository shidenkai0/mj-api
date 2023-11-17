import uuid
import httpx
import pytest
from firebase_admin import auth

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
        "language": db_user.language,
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
async def test_create_user_invalid_language(client: httpx.AsyncClient):
    jwt_token = generate_jwt_token(
        email=USER_EMAIL,
        user_id=str(USER_UID),
        is_email_verified=False,
    )
    client.headers["Authorization"] = f"Bearer {jwt_token}"
    response = await client.post(
        "/users",
        json={
            "email": USER_EMAIL,
            "name": "Test",
            "language": "invalid_language",
        },
    )
    assert response.status_code == 422
    assert response.json() == {
        'detail': [
            {
                'ctx': {'error': {}},
                'loc': ['body', 'language'],
                'input': 'invalid_language',
                'msg': 'Value error, Language invalid_language is not supported',
                'type': 'value_error',
                'url': 'https://errors.pydantic.dev/2.5/v/value_error',
            }
        ]
    }


@pytest.mark.asyncio
async def test_get_me(authenticated_client_user: httpx.AsyncClient, test_user: User):
    response = await authenticated_client_user.get("/users/me")
    assert response.status_code == 200
    assert response.json() == {
        "id": str(test_user.id),
        "email": test_user.email,
        "supabase_uid": test_user.supabase_uid,
        "name": test_user.name,
        "language": test_user.language,
    }
