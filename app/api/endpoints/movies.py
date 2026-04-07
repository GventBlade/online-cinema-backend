from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from app.api.crud import movie as movie_crud
from app.schemas import movies as movies_schema
from app.database import get_db
from app import models
from app.dependencies import get_moderator_or_admin

from typing import List, Optional

router = APIRouter(tags=["Movies"])

@router.patch("/{movie_id}", response_model=movies_schema.MovieResponse, status_code=status.HTTP_200_OK)
def update_movie(
    movie_id: int,
    movie_in: movies_schema.MovieUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_moderator_or_admin)
):
    db_movie = movie_crud.get_movie(db, movie_id=movie_id)
    if not db_movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    return movie_crud.update_movie(db=db, db_movie=db_movie, movie_in=movie_in)


@router.delete("/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_movie(movie_id: int, db: Session = Depends(get_db),
                 current_user: models.User = Depends(get_moderator_or_admin)):
    db_movie = movie_crud.get_movie(db, movie_id=movie_id)
    if not db_movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    movie_crud.delete_movie(db=db, db_movie=db_movie)
    return None


@router.get("/{movie_id}", response_model=movies_schema.MovieResponse)
def get_movie(movie_id: int, db: Session = Depends(get_db),):
    db_movie = movie_crud.get_movie(db, movie_id=movie_id)
    if not db_movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return db_movie


@router.get("/", response_model=List[movies_schema.MovieResponse])
def read_movies(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 10,
    search: Optional[str] = Query(None, description="Search by title, description, star, or director"),
    year: Optional[int] = Query(None),
    min_rating: Optional[float] = Query(None, ge=0, le=10),
    max_rating: Optional[float] = Query(None, ge=0, le=10),
    genre_id: Optional[int] = Query(None),
    sort_by: str = Query("year", enum=["price", "year", "rating", "popularity"]),
    order: str = Query("desc", enum=["asc", "desc"])
):
    return movie_crud.get_movies(
        db=db, skip=skip, limit=limit, search=search, year=year,
        min_rating=min_rating, max_rating=max_rating,
        genre_id=genre_id, sort_by=sort_by, order=order
    )
