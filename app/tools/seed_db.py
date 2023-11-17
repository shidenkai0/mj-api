import asyncio
import uuid
from datetime import datetime

import firebase_admin
from firebase_admin import auth, credentials

from app.config import settings
from app.user.models import User

cred = credentials.Certificate(settings.FIREBASE_KEY_FILE)
firebase_admin.initialize_app(cred)


async def create_user(email: str, supabase_uid: str, name: str, language: str, is_superuser: bool) -> User:
    user = await User.create(
        email=email, supabase_uid=supabase_uid, name=name, language=language, is_superuser=is_superuser
    )
    return user


async def seed_db():
    # Create user in firebase
    firebase_user = auth.create_user(email="testuser@example.com", password="stpzga8n", email_verified=True)

    # Create user in DB
    user = await create_user(
        email="testuser@example.com",
        supabase_uid=firebase_user.uid,
        name="Testuser",
        language="en",
        is_superuser=False,
    )


asyncio.run(seed_db())
