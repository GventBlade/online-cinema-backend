from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.dependencies import get_current_user
from app.api.crud import cart as cart_crud
from app.schemas.cart import CartResponse
from app import models
from app.database import get_db

router = APIRouter()

@router.get("/", response_model=CartResponse, status_code=status.HTTP_200_OK)
def read_user_cart(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return cart_crud.get_user_cart(db, user_id=current_user.id)


@router.post("/add/{movie_id}", response_model=CartResponse, status_code=status.HTTP_201_CREATED)
def add_to_cart(
    movie_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    cart_crud.add_movie_to_cart(db, user_id=current_user.id, movie_id=movie_id)
    return cart_crud.get_user_cart(db, user_id=current_user.id)


@router.delete("/remove/{movie_id}", status_code=status.HTTP_200_OK)
def remove_from_cart(
    movie_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return cart_crud.remove_from_cart(db, user_id=current_user.id, movie_id=movie_id)
