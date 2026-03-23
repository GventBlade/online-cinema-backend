import enum
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Enum, Text, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class UserGroupEnum(str, enum.Enum):
    USER = "USER"
    ADMIN = "ADMIN"
    MODERATOR = "MODERATOR"


class GenderEnum(str, enum.Enum):
    MAN = "MAN"
    WOMAN = "WOMAN"


class UserGroup(Base):
    __tablename__ = "user_groups"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(Enum(UserGroupEnum), nullable=False, unique=True)

    users = relationship("User", back_populates="group")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    group_id = Column(Integer, ForeignKey("user_groups.id"))

    group = relationship("UserGroup", back_populates="users")
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    activation_token = relationship("ActivationToken", back_populates="user", uselist=False,
                                    cascade="all, delete-orphan")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")


class UserProfile(Base):
    __tablename__ = "user_profiles"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    gender = Column(Enum(GenderEnum), nullable=True)
    info = Column(Text, nullable=True)

    user = relationship("User", back_populates="profile")


class ActivationToken(Base):
    __tablename__ = "activation_tokens"
    id = Column(Integer, primary_key=True, index=True, unique=True)
    token = Column(String, unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)

    users_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    user = relationship("User", back_populates="activation_token")


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, nullable=False, index=True, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)

    users_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    user = relationship("User", back_populates="refresh_tokens")


movie_genres = Table("movie_genres", Base.metadata,
                     Column("movie_id", Integer, ForeignKey("movies.id", ondelete="CASCADE"), primary_key=True),
                     Column("genre_id", Integer, ForeignKey("genres.id", ondelete="CASCADE"), primary_key=True),
                     )

movie_actors = Table("movie_actors", Base.metadata,
                     Column("movie_id", Integer, ForeignKey("movies.id", ondelete="CASCADE"), primary_key=True),
                     Column("actor_id", Integer, ForeignKey("actors.id", ondelete="CASCADE"), primary_key=True),
                     )


class Genre(Base):
    __tablename__ = "genres"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    movies = relationship("Movie", secondary=movie_genres, back_populates="genres")


class Actor(Base):
    __tablename__ = "actors"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    birth_date = Column(DateTime, nullable=False)
    movies = relationship("Movie",secondary=movie_actors, back_populates="actors")


class Movie(Base):
    __tablename__ = "movies"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    release_date = Column(DateTime(timezone=True), nullable=False)
    duration = Column(Integer, nullable=False)

    genres = relationship("Genre", secondary=movie_genres,  back_populates="movies")
    actors = relationship("Actor", secondary=movie_actors,  back_populates="movies")

    image_url = Column(String, nullable=True)