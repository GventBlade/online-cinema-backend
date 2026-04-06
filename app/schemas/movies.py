from decimal import Decimal
from typing import Optional, Annotated, List

from pydantic import BaseModel, ConfigDict, Field



class NameBase(BaseModel):
    name: str

class IdResponse(BaseModel):
    id: int
    model_config = ConfigDict(from_attributes=True)



class GenreCreate(NameBase): pass


class GenreResponse(NameBase, IdResponse): pass


class StarCreate(NameBase): pass


class StarResponse(NameBase, IdResponse): pass


class DirectorCreate(NameBase): pass


class DirectorResponse(NameBase, IdResponse): pass


class CertificationCreate(NameBase): pass


class CertificationResponse(NameBase, IdResponse): pass


class MovieBase(BaseModel):
    name: str
    year: Annotated[int, Field(ge=1895, le=2100)]
    time: Annotated[int, Field(gt=0, le=1000)]
    imdb: Annotated[float, Field(ge=0, le=10)]
    votes: int
    meta_score: Optional[float] = None
    gross: Optional[float] = None
    description: str
    price: Annotated[Decimal, Field(gt=0, le=1000)]


class MovieCreate(MovieBase):
    certification_id: int
    genre_ids: List[int]
    star_ids: List[int]
    director_ids: List[int]


class MovieResponse(MovieBase, IdResponse):
    uuid: str
    certification: CertificationResponse
    genres: List[GenreResponse]
    stars: List[StarResponse]
    directors: List[DirectorResponse]


class MovieUpdate(BaseModel):
    name: Optional[str] = None
    year: Annotated[Optional[int], Field(ge=1895, le=2100)] = None
    time: Annotated[Optional[int], Field(gt=0, le=1000)] = None
    imdb: Annotated[Optional[float], Field(ge=0, le=10)] = None
    votes: Optional[int] = None
    meta_score: Optional[float] = None
    gross: Optional[float] = None
    description: Optional[str] = None
    price: Annotated[Optional[Decimal], Field(gt=0, le=1000)] = None

    certification_id: Optional[int] = None
    genre_ids: Optional[List[int]] = None
    star_ids: Optional[List[int]] = None
    director_ids: Optional[List[int]] = None
