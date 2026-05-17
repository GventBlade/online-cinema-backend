from sqlalchemy.orm import Session
from sqlalchemy import func
from app import models
from app.schemas import movies as schemas
from app.schemas.base import ReactionEnum


def toggle_favorite(db: Session, user_id: int, movie_id: int):
    db_favorite = (
        db.query(models.Favorite)
        .filter(
            models.Favorite.user_id == user_id,
            models.Favorite.movie_id == movie_id,
        )
        .first()
    )

    if db_favorite:
        db.delete(db_favorite)
        db.commit()
        return {"status": "removed"}

    new_favorite = models.Favorite(user_id=user_id, movie_id=movie_id)
    db.add(new_favorite)
    db.commit()
    return {"status": "added"}


def set_movie_reaction(
    db: Session, user_id: int, movie_id: int, reaction: ReactionEnum
):
    db_reaction = (
        db.query(models.MovieReaction)
        .filter(
            models.MovieReaction.user_id == user_id,
            models.MovieReaction.movie_id == movie_id,
        )
        .first()
    )

    if db_reaction:
        if db_reaction.reaction == reaction:
            db.delete(db_reaction)
            db.commit()
            return None
        db_reaction.reaction = reaction

    else:
        db_reaction = models.MovieReaction(
            user_id=user_id, movie_id=movie_id, reaction=reaction
        )
        db.add(db_reaction)

    db.commit()
    db.refresh(db_reaction)
    return db_reaction


def rate_movie(db: Session, user_id: int, movie_id: int, score: int):
    db_rating = (
        db.query(models.Rating)
        .filter(
            models.Rating.user_id == user_id,
            models.Rating.movie_id == movie_id,
        )
        .first()
    )

    if db_rating:
        db_rating.score = score

    else:
        db_rating = models.Rating(user_id=user_id, movie_id=movie_id, score=score)
        db.add(db_rating)

    db.commit()
    db.refresh(db_rating)
    return db_rating


def create_reply_notification(db: Session, comment: models.Comment):
    parent_comment = (
        db.query(models.Comment).filter(models.Comment.id == comment.parent_id).first()
    )
    if parent_comment and parent_comment.user_id != comment.user_id:
        notification = models.Notification(
            user_id=parent_comment.user_id,
            message=f"The user left a reply for your comment {comment.text[:30]}...",
        )
        db.add(notification)
        db.commit()


def create_comment(
    db: Session, user_id: int, movie_id: int, comment_in: schemas.CommentCreate
):
    if comment_in.parent_id:
        parent = (
            db.query(models.Comment)
            .filter(models.Comment.id == comment_in.parent_id)
            .first()
        )
        if not parent:
            comment_in.parent_id = None

    db_comment = models.Comment(
        text=comment_in.text,
        user_id=user_id,
        movie_id=movie_id,
        parent_id=comment_in.parent_id,
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)

    if db_comment.parent_id:
        create_reply_notification(db, db_comment)

    return db_comment


def get_movie_comments(db: Session, movie_id: int):
    return (
        db.query(models.Comment)
        .filter(
            models.Comment.movie_id == movie_id,
            models.Comment.parent_id.is_(None),
        )
        .all()
    )


def get_movie_average_rating(db: Session, movie_id: int):
    result = (
        db.query(func.avg(models.Rating.score))
        .filter(models.Rating.movie_id == movie_id)
        .scalar()
    )
    if result is None:
        return 0.0
    return round(float(result), 1)
