from fastapi import HTTPException
from sqlalchemy.orm import Session
from app import models, security
from app.schemas import users as users_schema
from datetime import datetime, timedelta, timezone
import secrets

from app.schemas.base import UserGroupEnum


def get_user_by_email(db: Session ,email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session ,user_in: users_schema.UserCreate)-> tuple[models.User, str]:
    hashed_password = security.get_password_hash(user_in.password)
    db_user = models.User(
        email=user_in.email,
        hashed_password=hashed_password,
        is_active=False,
    )
    db.add(db_user)
    db.flush()

    db_profile = models.UserProfile(user_id=db_user.id)
    db.add(db_profile)

    token_value = secrets.token_urlsafe(32)
    db_token = models.ActivationToken(
        token=token_value,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
        users_id = db_user.id
    )
    db.add(db_token)

    db.commit()
    db.refresh(db_user)
    return db_user, token_value


def activate_user_account(db: Session, token: str):
    db_token = db.query(models.ActivationToken).filter(models.ActivationToken.token == token).first()
    if not db_token:
        raise HTTPException(status_code=404, detail="Invalid token")

    now = datetime.now(timezone.utc)
    if db_token.expires_at.replace(tzinfo=timezone.utc) < now:
        db.delete(db_token)
        db.commit()
        return False

    user = db_token.user
    user.is_active = True

    user_group = db.query(models.UserGroup).filter(models.UserGroup.name == UserGroupEnum.USER).first()
    if user_group:
        user.group_id = user_group.id

    db.delete(db_token)
    db.commit()
    db.refresh(user)

    return user

def create_refresh_token_entry(db: Session, user_id: int, token: str, expires_at: datetime):
    db_refresh_token = models.RefreshToken(
        token=token,
        users_id=user_id,
        expires_at=expires_at,
    )
    db.add(db_refresh_token)
    db.commit()
    db.refresh(db_refresh_token)

    return db_refresh_token

def get_refresh_token(db: Session, token: str):
    return db.query(models.RefreshToken).filter(models.RefreshToken.token == token).first()


def delete_refresh_token(db: Session, token: str):
    db_token = get_refresh_token(db, token)
    if db_token:
        db.delete(db_token)
        db.commit()
        return True
    return False


def create_password_reset_token(db: Session, user_id: int):
    token_value = secrets.token_urlsafe(32)
    db_reset_token = models.PasswordResetToken(
        password_reset_token=token_value,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
        users_id = user_id,
    )
    db.add(db_reset_token)
    db.commit()
    db.refresh(db_reset_token)

    return db_reset_token


def reset_password_with_token(db: Session, token_value: str, new_password: str):
    db_token = db.query(models.PasswordResetToken).filter(models.PasswordResetToken.password_reset_token == token_value).first()
    if not db_token:
        return None

    if db_token.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        db.delete(db_token)
        db.commit()
        return False

    user = db_token.user
    user.hashed_password = security.get_password_hash(new_password)

    db.delete(db_token)
    db.commit()
    db.refresh(user)

    return user

def delete_reset_token(db: Session, token: str):
    db_token = db.query(models.PasswordResetToken).filter(models.PasswordResetToken.password_reset_token == token).first()
    if db_token:
        db.delete(db_token)
        db.commit()
        return True
    return False


def update_user_password(db: Session, user: models.User, new_password: str):
    user.hashed_password = security.get_password_hash(new_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
