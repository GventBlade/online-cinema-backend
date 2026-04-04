from decimal import Decimal
from typing import Optional, Annotated, List

from pydantic import BaseModel, ConfigDict, field_validator, Field
from pydantic_core.core_schema import ValidationInfo


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
