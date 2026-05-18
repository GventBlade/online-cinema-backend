from fastapi import HTTPException
from sqlalchemy.orm import Session
from app import models
from app.models import (
    Genre,
    Star,
    Director,
    Certification,
    Movie,
    OrderItem,
    Order,
    OrderStatusEnum,
)
from app.schemas import movies as movies_schema

from sqlalchemy import or_, func
from typing import Optional


def create_genre(db: Session, genre_in: movies_schema.GenreCreate) -> Genre:
    db_genre = Genre(name=genre_in.name)
    db.add(db_genre)
    db.commit()
    db.refresh(db_genre)
    return db_genre


def create_star(db: Session, star_in: movies_schema.StarCreate) -> Star:
    db_star = Star(name=star_in.name)
    db.add(db_star)
    db.commit()
    db.refresh(db_star)
    return db_star


def create_director(db: Session, director_in: movies_schema.DirectorCreate) -> Director:
    db_director = Director(name=director_in.name)
    db.add(db_director)
    db.commit()
    db.refresh(db_director)
    return db_director


def create_certification(
    db: Session, cert_in: movies_schema.CertificationCreate
) -> Certification:
    db_certification = Certification(name=cert_in.name)
    db.add(db_certification)
    db.commit()
    db.refresh(db_certification)
    return db_certification


def create_movie(db: Session, movie_in: movies_schema.MovieCreate) -> Movie:
    existing_movie = (
        db.query(Movie)
        .filter(
            Movie.name == movie_in.name,
            Movie.year == movie_in.year,
            Movie.time == movie_in.time,
        )
        .first()
    )

    if existing_movie:
        raise HTTPException(
            status_code=400,
            detail=f"Movie with name '{movie_in.name}',"
            f" year {movie_in.year} and duration {movie_in.time} already exists.",
        )
    genres = db.query(Genre).filter(Genre.id.in_(movie_in.genre_ids)).all()
    stars = db.query(Star).filter(Star.id.in_(movie_in.star_ids)).all()
    directors = db.query(Director).filter(Director.id.in_(movie_in.director_ids)).all()

    if len(genres) != len(movie_in.genre_ids):
        raise HTTPException(status_code=400, detail="One or more genres not found")
    if len(stars) != len(movie_in.star_ids):
        raise HTTPException(status_code=400, detail="One or more stars not found")
    if len(directors) != len(movie_in.director_ids):
        raise HTTPException(status_code=400, detail="One or more directors not found")

    db_movie = Movie(
        **movie_in.model_dump(exclude={"genre_ids", "star_ids", "director_ids"}),
        genres=genres,
        stars=stars,
        directors=directors,
    )
    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)
    return db_movie


def get_movie(db: Session, movie_id: int):
    return db.query(Movie).filter(Movie.id == movie_id).first()


def get_movies(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    search: Optional[str] = None,
    year: Optional[int] = None,
    min_rating: Optional[float] = None,
    max_rating: Optional[float] = None,
    genre_id: Optional[int] = None,
    sort_by: str = "year",
    order: str = "desc",
    user_id: Optional[int] = None,
):
    query = db.query(models.Movie)

    if user_id:

        query = query.join(models.Favorite).filter(models.Favorite.user_id == user_id)

    if search:
        query = query.filter(
            or_(
                models.Movie.name.ilike(f"%{search}%"),
                models.Movie.description.ilike(f"%{search}%"),
                models.Movie.stars.any(models.Star.name.ilike(f"%{search}%")),
                models.Movie.directors.any(models.Director.name.ilike(f"%{search}%")),
                models.Movie.genres.any(models.Genre.name.ilike(f"%{search}%")),
            )
        )

    if year:
        query = query.filter(models.Movie.year == year)

    if min_rating:
        query = query.filter(models.Movie.imdb >= min_rating)

    if max_rating:
        query = query.filter(models.Movie.imdb <= max_rating)

    if genre_id:
        query = query.filter(models.Movie.genres.any(models.Genre.id == genre_id))

    sort_options = {
        "price": models.Movie.price,
        "year": models.Movie.year,
        "rating": models.Movie.imdb,
        "popularity": models.Movie.votes,
    }

    sort_attr = sort_options.get(sort_by, models.Movie.year)

    if order == "desc":
        query = query.order_by(sort_attr.desc())
    else:
        query = query.order_by(sort_attr.asc())

    return query.offset(skip).limit(limit).all()


def update_movie(
    db: Session, db_movie: Movie, movie_in: movies_schema.MovieUpdate
) -> Movie:
    update_data = movie_in.model_dump(exclude_unset=True)
    if "genre_ids" in update_data:
        new_genres = (
            db.query(Genre).filter(Genre.id.in_(update_data["genre_ids"])).all()
        )
        if len(new_genres) != len(update_data["genre_ids"]):
            raise HTTPException(status_code=400, detail="One or more genres not found")
        db_movie.genres = new_genres
        del update_data["genre_ids"]

    if "star_ids" in update_data:
        new_stars = db.query(Star).filter(Star.id.in_(update_data["star_ids"])).all()
        if len(new_stars) != len(update_data["star_ids"]):
            raise HTTPException(status_code=400, detail="One or more stars not found")
        db_movie.stars = new_stars
        del update_data["star_ids"]

    if "director_ids" in update_data:
        new_directors = (
            db.query(Director)
            .filter(Director.id.in_(update_data["director_ids"]))
            .all()
        )
        if len(new_directors) != len(update_data["director_ids"]):
            raise HTTPException(
                status_code=400, detail="One or more directors not found"
            )
        db_movie.directors = new_directors
        del update_data["director_ids"]

    for field, value in update_data.items():
        setattr(db_movie, field, value)

    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)
    return db_movie


def delete_movie(db: Session, db_movie: Movie):
    purchased = (
        db.query(OrderItem)
        .join(Order)
        .filter(
            OrderItem.movie_id == db_movie.id,
            Order.status == OrderStatusEnum.PAID,
        )
        .first()
    )
    if purchased:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete movie: it has already been purchased by users.",
        )

    db.delete(db_movie)
    db.commit()
    return db_movie


def get_genres(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Genre).offset(skip).limit(limit).all()


def get_directors(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Director).offset(skip).limit(limit).all()


def get_stars(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Star).offset(skip).limit(limit).all()


def get_genres_with_count(db: Session):
    return (
        db.query(models.Genre, func.count(models.Movie.id).label("movies_count"))
        .outerjoin(models.Movie.genres)
        .group_by(models.Genre.id)
        .all()
    )
