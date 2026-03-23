from pydantic import BaseModel, ConfigDict
import datetime
from typing import Optional

from app.schemas.base import GenderEnum


class GenreResponse(BaseModel):
    id: int
    name: str
    movie_ids: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class ActorResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    birth_date: Optional[datetime.date]
    gender: Optional[GenderEnum]
    movie_ids: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class MovieCreate(BaseModel):
    id: int
    title: str
    description: str