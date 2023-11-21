from fastapi import APIRouter, HTTPException, status

from app.user.auth import ValidToken, ActiveVerifiedUser
from app.user.models import User
from app.user.schemas import UserCreate, UserRead

router = APIRouter(
    responses={404: {"description": "Not found"}},
    tags=["users"],
)


@router.post(
    "",
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "User already registered"},
    },
)
async def create_user(user_create: UserCreate, decoded_token: ValidToken) -> UserRead:
    supabase_uid = decoded_token.get("sub")

    db_user = await User.get_by_supabase_uid(supabase_uid)
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already registered")

    db_user = await User.create(
        email=user_create.email,
        supabase_uid=supabase_uid,
        name=user_create.name,
        is_superuser=False,
    )

    return UserRead(
        id=db_user.id,
        email=db_user.email,
        supabase_uid=supabase_uid,
        name=db_user.name,
    )


@router.get("/me", response_model=UserRead)
async def get_me(user: ActiveVerifiedUser) -> UserRead:
    """
    Get the current user.
    """
    return UserRead(
        id=user.id,
        email=user.email,
        supabase_uid=user.supabase_uid,
        name=user.name,
    )
