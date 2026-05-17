from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models import Order, OrderItem, OrderStatusEnum, Cart, CartItem, Movie
from sqlalchemy.orm import joinedload


def check_if_movie_purchased(db: Session, user_id: int, movie_id: int) -> bool:
    purchased_movie = (
        db.query(OrderItem)
        .join(Order)
        .filter(
            Order.user_id == user_id,
            Order.status == OrderStatusEnum.PAID,
            OrderItem.movie_id == movie_id,
        )
        .first()
    )
    return purchased_movie is not None


def add_movie_to_cart(db: Session, user_id: int, movie_id: int):
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    if not cart:
        cart = Cart(
            user_id=user_id,
        )
        db.add(cart)
        db.flush()

    if check_if_movie_purchased(db, user_id, movie_id):
        raise HTTPException(
            status_code=400,
            detail="Repeat purchases are not allowed. You already own this movie.",
        )

    already_in_cart = (
        db.query(CartItem)
        .filter(CartItem.cart_id == cart.id, CartItem.movie_id == movie_id)
        .first()
    )

    if already_in_cart:
        raise HTTPException(
            status_code=400, detail="This movie is already in your cart"
        )

    new_item = CartItem(
        cart_id=cart.id,
        movie_id=movie_id,
    )
    db.add(new_item)

    try:
        db.commit()
        db.refresh(new_item)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Could not add movie to cart")

    return new_item


def get_user_cart(db: Session, user_id: int):
    cart = (
        db.query(Cart)
        .options(
            joinedload(Cart.items).joinedload(CartItem.movie).joinedload(Movie.genres)
        )
        .filter(Cart.user_id == user_id)
        .first()
    )
    if not cart:
        return {"items": [], "total_price": 0.0}

    total_price = sum(item.movie.price for item in cart.items)

    return {"items": cart.items, "total_price": total_price}


def remove_from_cart(db: Session, user_id: int, movie_id: int):
    item = (
        db.query(CartItem)
        .join(Cart)
        .filter(Cart.user_id == user_id, CartItem.movie_id == movie_id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Item not found in cart")

    db.delete(item)
    db.commit()
    return {"detail": "Item removed from cart"}


def clear_cart(db: Session, user_id: int):
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    if cart:
        db.query(CartItem).filter(CartItem.cart_id == cart.id).delete(
            synchronize_session=False
        )
        db.commit()
