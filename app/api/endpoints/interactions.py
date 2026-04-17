from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.crud import interactions as interactions_crud
from app.schemas import movies as movies_schema
from app.database import get_db
from app import models
from app.dependencies import get_current_user


router = APIRouter(tags=["Movies"])


def get_movie(db: Session, movie_id: int):
    movie = db.query(models.Movie).filter(models.Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")
    return movie


@router.post("/{movie_id}/favorite", status_code=status.HTTP_200_OK)
def create_favorite(movie_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)):
    get_movie(db, movie_id)

    return interactions_crud.toggle_favorite(db=db, movie_id=movie_id, user_id=current_user.id)


@router.post("/{movie_id}/react", status_code=status.HTTP_200_OK)
def set_reaction(
    movie_id: int,
    reaction_in: movies_schema.ReactionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
                 ):
    get_movie(db, movie_id)
    return interactions_crud.set_movie_reaction(
        db=db, user_id=current_user.id,movie_id=movie_id,reaction=reaction_in.reaction
    )

@router.post("/{movie_id}/rate", status_code=status.HTTP_200_OK)
def rate_movie(
    movie_id: int,
    score_in: movies_schema.RatingCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    get_movie(db, movie_id)
    return interactions_crud.rate_movie(db=db, movie_id=movie_id, user_id=current_user.id, score=score_in.score)


@router.post("/{movie_id}/comments", status_code=status.HTTP_201_CREATED)
def create_comment(
    movie_id: int,
    comment_in: movies_schema.CommentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    get_movie(db, movie_id)
    return interactions_crud.create_comment(db=db,user_id=current_user.id, movie_id=movie_id, comment_in=comment_in)

@router.get("/{movie_id}/comments", status_code=status.HTTP_200_OK)
def get_comments(
    movie_id: int,
    db: Session = Depends(get_db),
):
    get_movie(db, movie_id)
    return interactions_crud.get_movie_comments(db=db, movie_id=movie_id)


@router.get("/{movie_id}/rating", response_model=movies_schema.MovieAverageRatingResponse)
def get_movie_rating(
    movie_id: int,
    db: Session = Depends(get_db),
):
    get_movie(db, movie_id)
    average = interactions_crud.get_movie_average_rating(db=db, movie_id=movie_id)
    return {"movie_id": movie_id, "average": average}


