import asyncio
import argparse
from supabase import create_client, Client

from app.config import settings
from app.user.models import User

supabase: Client = create_client(supabase_url=settings.SUPABASE_URL, supabase_key=settings.SUPABASE_SERVICE_ROLE_KEY)

TEST_USER_EMAIL = "testuser@example.com"
TEST_USER_PASSWORD = "stpzga8n"


async def seed_db():
    # Create user in Supabase
    resp = supabase.auth.admin.create_user(
        {"email": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD, "email_confirm": True}
    )


async def cleanup_db():
    # Delete user in Supabase
    users = supabase.auth.admin.list_users(page=1, per_page=20)
    # Find user by email
    test_user = [user for user in users if user.email == TEST_USER_EMAIL].pop()
    user_id = test_user.id
    resp = supabase.auth.admin.delete_user(user_id)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed Supabase database")
    parser.add_argument("--cleanup", action="store_true", help="Cleanup Supabase database")

    args = parser.parse_args()

    if args.cleanup:
        asyncio.run(cleanup_db())
    else:
        asyncio.run(seed_db())
