from datetime import datetime
from decimal import Decimal
from typing import List

from app.models import OrderStatusEnum
from pydantic import BaseModel, ConfigDict

from app.schemas.movies import GenreResponse


class MovieCartInfo(BaseModel):
    id: int
    name: str
    price: Decimal
    year: int
    genres: List[GenreResponse]


class CartItemResponse(BaseModel):
    id: int
    added_at: datetime
    movie : MovieCartInfo

    model_config = ConfigDict(from_attributes=True)


class CartItemCreate(BaseModel):
    movie_id: int


class CartResponse(BaseModel):
    items: List[CartItemResponse]
    total_price: Decimal

    model_config = ConfigDict(from_attributes=True)


class OrderItemResponse(BaseModel):
    id: int
    movie : MovieCartInfo
    price_at_order : Decimal

    model_config = ConfigDict(from_attributes=True)


class OrderResponse(BaseModel):
    id: int
    created_at: datetime
    status: OrderStatusEnum
    total_amount: Decimal
    items: List[OrderItemResponse]

    model_config = ConfigDict(from_attributes=True)


class PurchaseMovieResponse(BaseModel):
    movie: MovieCartInfo
    purchase_date: datetime

