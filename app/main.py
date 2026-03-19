from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, security
from app.database import engine, get_db
from app.schemas import users as user_schemas

from datetime import datetime, timedelta, timezone
import secrets

app = FastAPI(title="Online Cinema API")


@app.post("/register", response_model=user_schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_data: user_schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user_data.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = security.get_password_hash(user_data.password)

    new_user = models.User(
        email=user_data.email,
        hashed_password=hashed_password,
    )
    db.add(new_user)
    db.flush()

    token_value = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=24)

    activation_token = models.ActivationToken(
        token=token_value,
        expires_at=expires_at,
        users_id=new_user.id,
    )
    db.add(activation_token)
    db.commit()
    db.refresh(new_user)

    print(f"Token for {new_user.email}: {token_value}")

    return new_user


@app.get("/activate", status_code=status.HTTP_200_OK)
def activate_user(token: str, db: Session = Depends(get_db)):
    db_token = db.query(models.ActivationToken).filter(models.ActivationToken.token == token).first()
    if not db_token:
        raise HTTPException(status_code=404, detail="Activation token not found")
    if db_token.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        db.delete(db_token)
        db.commit()
        raise HTTPException(status_code=400, detail="Activation token not expired")

    user = db_token.user
    user.is_active = True
    db.delete(db_token)
    db.commit()

    return {"Message": "Account activated successfully"}


@app.post("/login", response_model=user_schemas.Token, status_code=status.HTTP_200_OK)
def user_login(user_data: user_schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user_data.email).first()
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    user_password = security.verify_password(user_data.password, db_user.hashed_password)
    if not user_password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not db_user.is_active:
        raise HTTPException(status_code=401, detail="Inactive user")
    access_token = security.create_access_token(data={"sub": user_data.email})
    refresh_token = security.create_refresh_token(data={"sub": user_data.email})
    expired_at = datetime.now(timezone.utc) + timedelta(days=security.REFRESH_TOKEN_EXPIRE_DAYS)

    db_refresh_token =  models.RefreshToken(
        token=refresh_token,
        users_id=db_user.id,
        expires_at=expired_at,
    )
    db.add(db_refresh_token)
    db.commit()

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "Bearer"}
