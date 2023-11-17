from datetime import datetime, timedelta
from typing import AsyncGenerator, Generator
import uuid

import httpx
import jwt
import pytest_asyncio
from fastapi import FastAPI
from firebase_admin import auth

from app.app import create_app
from app.config import settings
from app.user.auth import ActiveVerifiedUser, SuperUser
from app.user.models import User


@pytest_asyncio.fixture(autouse=True)
def test_app() -> Generator[FastAPI, None, None]:
    """
    Test the FastAPI app.
    """
    app = create_app()

    @app.get("/verifieduser")
    async def get_active_user(user: ActiveVerifiedUser):
        return {"id": user.id, "email": user.email}

    @app.get("/superuser")
    async def get_superuser(user: SuperUser):
        return {"id": user.id, "email": user.email}

    yield app


HOST, PORT = "127.0.0.1", "8080"


# Generate JWT Token for Test User
def generate_jwt_token(user_id: str, email: str, is_email_verified: bool = True) -> str:
    payload = {
        "sub": user_id,
        "email": email,
        "email_verified": is_email_verified,
        "exp": datetime.utcnow() + timedelta(hours=1),
    }
    token = jwt.encode(payload, settings.SUPABASE_JWT_SECRET, algorithm="HS256")
    return token


# Create Test User in Database
async def create_test_user(email: str, name: str, is_superuser: bool) -> User:
    user = await User.create(
        email=email,
        supabase_uid=str(uuid.uuid4()),  # Generate a unique ID
        name=name,
        language="en",
        is_superuser=is_superuser,
    )
    assert user.id is not None
    return user


@pytest_asyncio.fixture
async def test_user() -> AsyncGenerator[User, None]:
    user = await create_test_user(email="user@test.com", name="Test User", is_superuser=False)
    yield user


@pytest_asyncio.fixture
async def test_unverified_user() -> AsyncGenerator[User, None]:
    user = await create_test_user(email="unverified@test.com", name="Test Unverified User", is_superuser=False)
    yield user


@pytest_asyncio.fixture
async def test_superuser() -> AsyncGenerator[User, None]:
    user = await create_test_user(email="superuser@test.com", name="Test Superuser", is_superuser=True)
    yield user


@pytest_asyncio.fixture
async def client(test_app: FastAPI) -> AsyncGenerator[httpx.AsyncClient, None]:
    host, port = HOST, PORT
    async with httpx.AsyncClient(
        app=test_app, base_url=f"http://{host}:{port}", headers={"X-User-Fingerprint": "Test"}
    ) as client:
        yield client


@pytest_asyncio.fixture
async def authenticated_client_user(
    client: httpx.AsyncClient, test_user: User
) -> AsyncGenerator[httpx.AsyncClient, None]:
    token = generate_jwt_token(test_user.supabase_uid, test_user.email)
    client.headers["Authorization"] = f"Bearer {token}"
    yield client


@pytest_asyncio.fixture
async def authenticated_client_unverified_user(
    client: httpx.AsyncClient, test_unverified_user: User
) -> AsyncGenerator[httpx.AsyncClient, None]:
    token = generate_jwt_token(test_unverified_user.supabase_uid, test_unverified_user.email, is_email_verified=False)
    client.headers["Authorization"] = f"Bearer {token}"
    yield client


@pytest_asyncio.fixture
async def authenticated_client_superuser(
    client: httpx.AsyncClient, test_superuser: User
) -> AsyncGenerator[httpx.AsyncClient, None]:
    token = generate_jwt_token(test_superuser.supabase_uid, test_superuser.email)
    client.headers["Authorization"] = f"Bearer {token}"
    yield client
