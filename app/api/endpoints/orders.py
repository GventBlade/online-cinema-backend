from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.dependencies import get_current_user
from app.api.crud import order as crud_order
from app.schemas.cart import OrderItemResponse, OrderResponse
from app import models
from app.database import get_db

router = APIRouter()

@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return crud_order.create_order(db, user_id=current_user.id)

@router.get("/", response_model=list[OrderResponse], status_code=status.HTTP_200_OK)
def get_my_orders(db: Session = Depends(get_db) ,current_user: models.User = Depends(get_current_user)):
    return crud_order.get_user_orders(db, user_id=current_user.id)

@router.get("/{order_id}", response_model=OrderResponse, status_code=status.HTTP_200_OK)
def get_order_details(order_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    order = crud_order.get_order_by_id(db, order_id=order_id, user_id=current_user.id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order


@router.patch("/{order_id}/cancel", response_model=OrderResponse, status_code=status.HTTP_202_ACCEPTED)
def cancel_order(order_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return crud_order.cancel_order(db, order_id=order_id, user_id=current_user.id)
