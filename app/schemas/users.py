from pydantic import BaseModel, EmailStr, ConfigDict, Field, field_validator
import re
from typing import Optional, Annotated, List

from datetime import datetime

from app.schemas.base import GenderEnum
from app.schemas import movies as movies_schemas


StrongPassword = Annotated[str, Field(min_length=8, max_length=64)]


class PasswordMixin(BaseModel):
    @field_validator("password", "new_password", mode="after", check_fields=False)
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one number")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain at least one special character")

        return v


class UserProfile(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar: Optional[str] = None
    gender: Optional[GenderEnum] = None
    date_of_birth: Optional[datetime] = None
    info: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class UserCreate(PasswordMixin):
    email: EmailStr
    password: StrongPassword


class UserGroupResponse(BaseModel):
    name: str

    model_config = ConfigDict(from_attributes=True)


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    is_active: bool
    group: Optional[UserGroupResponse] = None
    profile: Optional[UserProfile]

    favorites: List["movies_schemas.FavoriteResponse"] = []
    comments: List["movies_schemas.CommentResponse"] = []
    notifications: List["movies_schemas.NotificationsResponse"] = []

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


class TokenExchange(BaseModel):
    token: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class RequestEmail(BaseModel):
    email: EmailStr


class PasswordResetConfirm(PasswordMixin):
    token: str
    new_password: StrongPassword


class PasswordChange(PasswordMixin):
    old_password: str = Field(...)
    new_password: StrongPassword


UserResponse.model_rebuild(_types_namespace={"movies_schemas": movies_schemas})
