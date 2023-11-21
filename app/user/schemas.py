from uuid import UUID

from pydantic import field_validator, BaseModel, EmailStr

from app.config import settings


class UserCreate(BaseModel):
    email: EmailStr
    name: str


class UserRead(BaseModel):
    id: UUID
    email: EmailStr
    supabase_uid: UUID
    name: str
