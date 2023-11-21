import asyncio
from supabase import create_client, Client

from app.config import settings
from app.user.models import User

supabase: Client = create_client(supabase_url=settings.SUPABASE_URL, supabase_key=settings.SUPABASE_SERVICE_ROLE_KEY)


async def create_user(email: str, supabase_uid: str, name: str, language: str, is_superuser: bool) -> User:
    user = await User.create(
        email=email, supabase_uid=supabase_uid, name=name, language=language, is_superuser=is_superuser
    )
    return user


async def seed_db():
    USER_EMAIL = "testuser@example.com"
    USER_PASSWORD = "stpzga8n"

    # Create user in Supabase
    resp = supabase.auth.admin.create_user({"email": USER_EMAIL, "password": USER_PASSWORD, "email_confirm": True})

    # Get Supabase UID
    supabase_uid = resp.user.id

    # Create user in DB
    user = await create_user(
        email=USER_EMAIL,
        supabase_uid=supabase_uid,
        name="Testuser",
        language="en",
        is_superuser=False,
    )


asyncio.run(seed_db())
