from fastapi.params import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.schemas.base import UserGroupEnum
from app.security import SECRET_KEY, ALGORITHM
from app import database, models
from jose import jwt, JWTError
from fastapi import status, HTTPException

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_current_user(token: str = Depends(oauth2_scheme),
                     db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")

        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(models.User).filter(models.User.email == email).first()

    if not user:
        raise credentials_exception

    return user


def get_admin_user(current_user: models.User = Depends(get_current_user)):
    if not current_user.group or current_user.group.name != UserGroupEnum.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have admin permissions",
        )

    return current_user


def get_moderator_or_admin(current_user: models.User = Depends(get_current_user)):
    if not  current_user.group or current_user.group.name not in  [UserGroupEnum.MODERATOR, UserGroupEnum.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have moderator permissions",
        )
    return current_user
