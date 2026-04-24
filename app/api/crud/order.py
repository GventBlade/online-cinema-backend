from sqlalchemy import desc
from sqlalchemy.orm import Session, joinedload
from app.models import Order, OrderItem, OrderStatusEnum, Cart, CartItem
from app.api.crud.cart import get_user_cart, clear_cart # Імпортуємо твої напрацювання
from fastapi import HTTPException


def create_order(db: Session, user_id: int):
    cart_data = get_user_cart(db, user_id)
    if not cart_data:
        raise HTTPException(status_code=400, detail="Cart is empty")
    new_order = Order(
        user_id = user_id,
        status = OrderStatusEnum.PENDING,
        total_amount=cart_data["total_price"]
    )
    db.add(new_order)
    db.flush()

    for item in cart_data["items"]:
        order_item = OrderItem(
            order_id = new_order.id,
            movie_id = item.movie_id,
            price_at_order=item.movie.price
        )
        db.add(order_item)

    try:
        clear_cart(db, user_id)
        db.commit()
        db.refresh(new_order)

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Failed to create order")

    return new_order


def mark_order_as_paid(db: Session, order_id: int, user_id: int):
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == user_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.status != OrderStatusEnum.PENDING:
        raise HTTPException(status_code=400, detail="Order already paid or canceled")

    order.status = OrderStatusEnum.PAID

    try:
        db.commit()
        db.refresh(order)

    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Could not update order status")
    return order


def get_user_orders(db: Session, user_id: int):
    orders = db.query(Order).options(
        joinedload(Order.items).joinedload(OrderItem.movie)
    ).filter(Order.user_id == user_id).order_by(desc(Order.created_at)).all()
    return orders


def cancel_order(db: Session, order_id: int, user_id: int):
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == user_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.status == OrderStatusEnum.PAID:
        raise HTTPException(status_code=400, detail="Once paid, orders can only be canceled via a refund request.")

    if order.status == OrderStatusEnum.CANCELED:
        raise HTTPException(status_code=400, detail="Order is already canceled")

    order.status = OrderStatusEnum.CANCELED

    try:
        db.commit()
        db.refresh(order)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="Could not cancel order")

    return order
