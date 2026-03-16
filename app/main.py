from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, security
from app.database import engine, get_db
from app.schemas import users as user_schemas

models.Base.metadata.create_all(bind=engine)

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
    db.commit()
    db.refresh(new_user)

    return new_user