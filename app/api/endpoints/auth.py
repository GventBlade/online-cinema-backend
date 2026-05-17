from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone

from app import models, security
from app.database import get_db
from app.schemas import users as user_schemas
from app.dependencies import get_current_user
from app.api.crud import user as crud_user

router = APIRouter(tags=["Authentication"])


@router.post(
    "/register",
    response_model=user_schemas.UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_user(user_data: user_schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud_user.get_user_by_email(db, email=user_data.email)
    if db_user:
        raise HTTPException(status_code=409, detail="Email already registered")

    new_user, token_value = crud_user.create_user(db, user_in=user_data)

    db.refresh(new_user)

    print(f"DEBUG: Activation token for {new_user.email}: {token_value} ")

    return new_user


@router.get("/activate", status_code=status.HTTP_200_OK)
def activate_user(token: str, db: Session = Depends(get_db)):
    result = crud_user.activate_user_account(db, token=token)
    if result is None:
        raise HTTPException(status_code=404, detail="Activation token not found")

    if result is False:
        raise HTTPException(status_code=400, detail="Activation token has expired")

    return {"Message": "Account activated successfully"}


@router.post(
    "/login", response_model=user_schemas.Token, status_code=status.HTTP_200_OK
)
def user_login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    db_user = crud_user.get_user_by_email(db, email=form_data.username)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )
    user_password = security.verify_password(
        form_data.password, db_user.hashed_password
    )
    if not user_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )
    if not db_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Account not activated"
        )
    user_id_str = str(db_user.id)
    access_token = security.create_access_token(data={"sub": user_id_str})
    refresh_token = security.create_refresh_token(data={"sub": user_id_str})
    expired_at = datetime.now(timezone.utc) + timedelta(
        days=security.REFRESH_TOKEN_EXPIRE_DAYS
    )

    crud_user.create_refresh_token_entry(
        db, user_id=db_user.id, token=refresh_token, expires_at=expired_at
    )
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def user_logout(
    token_data: user_schemas.TokenExchange,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    db_token = crud_user.get_refresh_token(db, token=token_data.token)
    if not db_token or db_token.users_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Token not found or invalid"
        )

    crud_user.delete_refresh_token(db, token=token_data.token)

    return None


@router.post(
    "/refresh", response_model=user_schemas.Token, status_code=status.HTTP_200_OK
)
def refresh_token(
    token_data: user_schemas.TokenExchange, db: Session = Depends(get_db)
):
    db_token = crud_user.get_refresh_token(db, token=token_data.token)
    if not db_token:
        raise HTTPException(status_code=401, detail="Token not found")
    if db_token.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        crud_user.delete_refresh_token(db, token=token_data.token)
        raise HTTPException(status_code=401, detail="Token expired")

    user_id_str = str(db_token.users_id)

    new_access_token = security.create_access_token(data={"sub": user_id_str})
    new_refresh_token = security.create_refresh_token(data={"sub": user_id_str})

    new_expires_at = datetime.now(timezone.utc) + timedelta(
        days=security.REFRESH_TOKEN_EXPIRE_DAYS
    )

    crud_user.delete_refresh_token(db, token=token_data.token)
    crud_user.create_refresh_token_entry(
        db,
        user_id=db_token.users_id,
        token=new_refresh_token,
        expires_at=new_expires_at,
    )

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }


@router.post("/password-reset-request", status_code=status.HTTP_200_OK)
def password_reset(data: user_schemas.RequestEmail, db: Session = Depends(get_db)):
    user = crud_user.get_user_by_email(db, email=data.email)
    if not user:
        return {
            "message": "If an account with that email exists, a password reset link has been sent."
        }

    db_token = crud_user.create_password_reset_token(db, user_id=user.id)

    print(
        f"DEBUG: Password reset token for {user.email}: {db_token.password_reset_token}"
    )
    return {"message": "Password reset link sent to your email"}


@router.post("/password-reset-confirm", status_code=status.HTTP_200_OK)
def password_reset_confirm(
    data: user_schemas.PasswordResetConfirm, db: Session = Depends(get_db)
):
    user = crud_user.reset_password_with_token(
        db, token_value=data.token, new_password=data.new_password
    )
    if user is None:
        raise HTTPException(status_code=404, detail="Invalid password reset token")
    if user is False:
        raise HTTPException(status_code=400, detail="Password reset token has expired")

    return {
        "message": "Password changed successfully. You can now log in with your new password."
    }


@router.post("/password-change", status_code=status.HTTP_200_OK)
def change_password(
    data: user_schemas.PasswordChange,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if not security.verify_password(data.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect old password")

    crud_user.update_user_password(
        db, user=current_user, new_password=data.new_password
    )

    return {"message": "Password changed successfully"}


@router.post("/resend-activation", status_code=status.HTTP_200_OK)
def resend_activation_token(
    data: user_schemas.RequestEmail, db: Session = Depends(get_db)
):
    new_token = crud_user.refresh_activation_token(db, email=data.email)

    if new_token is None:
        return {"message": "If the account is not activated, a new link has been sent."}

    print(f"DEBUG: New Activation token for {data.email}: {new_token}")
    return {"message": "A new activation link has been sent to your email."}
