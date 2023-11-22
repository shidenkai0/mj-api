import httpx
import pytest

from app.user.models import User


@pytest.mark.asyncio
async def test_authenticate_user(authenticated_client_user: httpx.AsyncClient, test_user: User):
    response = await authenticated_client_user.get("/verifieduser")
    assert response.status_code == 200
    assert response.json() == {"id": str(test_user.id), "email": test_user.email}


@pytest.mark.asyncio
async def test_authenticate_unverified_user(authenticated_client_unverified_user: httpx.AsyncClient):
    response = await authenticated_client_unverified_user.get("/verifieduser")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_authenticate_superuser(authenticated_client_superuser: httpx.AsyncClient, test_superuser: User):
    response = await authenticated_client_superuser.get("/superuser")
    assert response.status_code == 200
    assert response.json() == {"id": str(test_superuser.id), "email": test_superuser.email}


@pytest.mark.asyncio
async def test_authenticate_superuser_unauthorized(authenticated_client_user: httpx.AsyncClient):
    response = await authenticated_client_user.get("/superuser")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_authenticate_user_no_token(client: httpx.AsyncClient):
    response = await client.get("/verifieduser")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_authenticate_user_invalid_token(client: httpx.AsyncClient):
    jwt_token = "invalid_token"
    client.headers["Authorization"] = f"Bearer {jwt_token}"
    response = await client.get("/verifieduser")
    assert response.status_code == 401
