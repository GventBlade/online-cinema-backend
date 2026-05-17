from fastapi import status
from app.models import Movie, Certification, User, UserGroup, UserGroupEnum


def test_get_movies_list_empty(client):
    response = client.get("/api/v1/movies")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_get_movie_by_id_success(client, db_session):
    cert = Certification(name="PG-13")
    db_session.add(cert)
    db_session.commit()
    db_session.refresh(cert)

    test_movie = Movie(
        name="Inception",
        year=2010,
        time=148,
        imdb=8.8,
        votes=2400000,
        description="A thief who steals corporate secrets through the use of dream-sharing technology.",
        price=149.99,
        certification_id=cert.id,
    )
    db_session.add(test_movie)
    db_session.commit()
    db_session.refresh(test_movie)

    response = client.get(f"/api/v1/movies/{test_movie.id}")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["name"] == "Inception"
    assert data["id"] == test_movie.id


def test_get_movie_by_id_not_found(client):
    response = client.get("/api/v1/movies/99999")

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_create_movie_as_anonymous_or_user_fails(client, db_session):
    movie_payload = {
        "name": "Interstellar",
        "year": 2014,
        "time": 169,
        "imdb": 8.7,
        "votes": 1900000,
        "description": "A team of explorers travel through a wormhole in space.",
        "price": 199.99,
        "certification_id": 1,
    }

    response = client.post("/api/v1/movies", json=movie_payload)

    assert response.status_code in [
        status.HTTP_401_UNAUTHORIZED,
        status.HTTP_403_FORBIDDEN,
    ]


def test_create_movie_as_admin_success(client, db_session):
    admin_group = (
        db_session.query(UserGroup)
        .filter(UserGroup.name == UserGroupEnum.ADMIN)
        .first()
    )
    if not admin_group:
        admin_group = UserGroup(name=UserGroupEnum.ADMIN)
        db_session.add(admin_group)
        db_session.commit()

    admin_user = User(
        email="admin_cinema@example.com",
        hashed_password="Fakehashpassword1231",
        is_active=True,
        group_id=admin_group.id,
    )
    db_session.add(admin_user)
    db_session.commit()

    cert = Certification(name="R")
    db_session.add(cert)
    db_session.commit()
    db_session.refresh(cert)

    movie_payload = {
        "name": "Interstellar",
        "year": 2014,
        "time": 169,
        "imdb": 8.7,
        "votes": 1900000,
        "description": "A team of explorers travel through a wormhole in space.",
        "price": 199.99,
        "certification_id": cert.id,
    }

    response = client.post("/api/v1/movies", json=movie_payload)

    print("\nMovie status response:", response.status_code)
    print("Response:", response.json())


def test_add_to_favorites_success(client, db_session):
    email = "favorite_tester@example.com"
    password = "SecurePassword123!"

    client.post("/api/v1/auth/register", json={"email": email, "password": password})
    user = db_session.query(User).filter(User.email == email).first()
    user.is_active = True
    db_session.commit()

    login_res = client.post(
        "/api/v1/auth/login", data={"username": email, "password": password}
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    cert = Certification(name="G")
    db_session.add(cert)
    db_session.commit()

    movie = Movie(
        name="The Matrix",
        year=1999,
        time=136,
        imdb=8.7,
        votes=2000000,
        description="A computer hacker learns from mysterious rebels about the true nature of his reality.",
        price=99.99,
        certification_id=cert.id,
    )
    db_session.add(movie)
    db_session.commit()
    db_session.refresh(movie)

    fav_payload = {"movie_id": movie.id}
    response = client.post(
        f"/api/v1/movies/{movie.id}/favorite", json=fav_payload, headers=headers
    )

    print("\nResponse added to favorite:", response.status_code, response.json())

    assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_200_OK]


def test_add_to_favorites_toggle_off_success(client, db_session):
    email = "duplicate_fav@example.com"
    password = "SecurePassword123!"

    client.post("/api/v1/auth/register", json={"email": email, "password": password})
    user = db_session.query(User).filter(User.email == email).first()
    user.is_active = True
    db_session.commit()

    login_res = client.post(
        "/api/v1/auth/login", data={"username": email, "password": password}
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    cert = db_session.query(Certification).first() or Certification(name="PG")
    if cert.id is None:
        db_session.add(cert)
        db_session.commit()

    movie = Movie(
        name="Avatar",
        year=2009,
        time=162,
        imdb=7.9,
        votes=1300000,
        description="A paraplegic Marine dispatched to the moon Pandora on a unique mission.",
        price=119.99,
        certification_id=cert.id,
    )
    db_session.add(movie)
    db_session.commit()
    db_session.refresh(movie)

    client.post(f"/api/v1/movies/{movie.id}/favorite", headers=headers)

    response = client.post(f"/api/v1/movies/{movie.id}/favorite", headers=headers)

    assert response.status_code == status.HTTP_200_OK
