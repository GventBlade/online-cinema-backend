import pytest
from fastapi import status
from app.models import Movie, Certification, User


def test_comments_workflow(client, db_session):
    email = "commenter_flow@example.com"
    password = "SecurePassword123!"

    client.post("/api/v1/auth/register", json={"email": email, "password": password})
    user = db_session.query(User).filter(User.email == email).first()
    user.is_active = True
    db_session.commit()

    login_res = client.post("/api/v1/auth/login", data={"username": email, "password": password})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    cert = Certification(name="PG-13_comments")
    db_session.add(cert)
    db_session.commit()

    movie = Movie(
        name="Interstellar Legend",
        year=2014,
        time=169,
        imdb=8.6,
        votes=100000,
        description="Test movie for comments workflow",
        price=9.99,
        certification_id=cert.id
    )
    db_session.add(movie)
    db_session.commit()
    db_session.refresh(movie)

    comment_payload = {
        "text": "This movie was absolutely brilliant!"
    }
    response_post = client.post(
        f"/api/v1/movies/{movie.id}/comments",
        json=comment_payload,
        headers=headers
    )

    assert response_post.status_code == status.HTTP_201_CREATED
    assert response_post.json()["text"] == "This movie was absolutely brilliant!"

    response_get = client.get(f"/api/v1/movies/{movie.id}/comments")

    assert response_get.status_code == status.HTTP_200_OK
    comments_list = response_get.json()

    assert len(comments_list) > 0
    assert comments_list[0]["text"] == "This movie was absolutely brilliant!"


def test_set_movie_reaction_success(client, db_session):
    email = "reactor@example.com"
    password = "SecurePassword123!"

    client.post("/api/v1/auth/register", json={"email": email, "password": password})
    user = db_session.query(User).filter(User.email == email).first()
    user.is_active = True
    db_session.commit()

    login_res = client.post("/api/v1/auth/login", data={"username": email, "password": password})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    cert = Certification(name="PG-13_react_unique")
    db_session.add(cert)
    db_session.commit()
    db_session.refresh(cert)

    movie = Movie(
        name="Reaction Movie", year=2026, time=120, imdb=7.0, votes=500,
        description="Reaction test", price=49.99, certification_id=cert.id
    )
    db_session.add(movie)
    db_session.commit()
    db_session.refresh(movie)

    reaction_payload = {"reaction": "LIKE"}
    response = client.post(f"/api/v1/movies/{movie.id}/react", json=reaction_payload, headers=headers)

    assert response.status_code == status.HTTP_200_OK


def test_rate_movie_success(client, db_session):
    email = "rater@example.com"
    password = "SecurePassword123!"

    client.post("/api/v1/auth/register", json={"email": email, "password": password})
    user = db_session.query(User).filter(User.email == email).first()
    user.is_active = True
    db_session.commit()

    login_res = client.post("/api/v1/auth/login", data={"username": email, "password": password})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    cert = Certification(name="PG-13_rate_unique")
    db_session.add(cert)
    db_session.commit()
    db_session.refresh(cert)

    movie = Movie(
        name="Rating Movie", year=2026, time=110, imdb=8.0, votes=600,
        description="Rating test", price=59.99, certification_id=cert.id
    )
    db_session.add(movie)
    db_session.commit()
    db_session.refresh(movie)

    rating_payload = {"score": 9}
    response_rate = client.post(f"/api/v1/movies/{movie.id}/rate", json=rating_payload, headers=headers)
    assert response_rate.status_code == status.HTTP_200_OK

    response_get = client.get(f"/api/v1/movies/{movie.id}/rating")
    assert response_get.status_code == status.HTTP_200_OK
    assert response_get.json()["average"] == 9.0
