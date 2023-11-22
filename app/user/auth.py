import jwt

from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.user.models import User
from app.config import settings

SUPABASE_SECRET_KEY = settings.SUPABASE_JWT_SECRET
ALGORITHM = "HS256"  # HS256 is the default algorithm for JWT

security = HTTPBearer(auto_error=False)


async def authenticate_user_token(creds: Annotated[HTTPAuthorizationCredentials, Depends(security)]) -> jwt.PyJWT:
    if creds is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    id_token = creds.credentials
    try:
        # Decoding the JWT token
        decoded_token = jwt.decode(id_token, SUPABASE_SECRET_KEY, algorithms=[ALGORITHM], audience="authenticated")
        return decoded_token
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except jwt.InvalidTokenError as e:
        print(f"JWT token invalid: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


async def authenticate_user(decoded_token: Annotated[str, Depends(authenticate_user_token)]) -> User:
    supabase_uid = decoded_token.get("sub")  # 'sub' usually contains the user ID
    if supabase_uid is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized")
        # Fetch the user from your database using the user_id
    user = await User.get_by_supabase_uid(supabase_uid)
    if user is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User not found")
    role = decoded_token.get("role")
    if role != "authenticated":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized")

    return user


async def authenticate_superuser(user: Annotated[User, Depends(authenticate_user)]) -> User:
    if not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized",
        )
    return user


ValidToken = Annotated[str, Depends(authenticate_user_token)]
ActiveVerifiedUser = Annotated[User, Depends(authenticate_user)]
SuperUser = Annotated[User, Depends(authenticate_superuser)]
