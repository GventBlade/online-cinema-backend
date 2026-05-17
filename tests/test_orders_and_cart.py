import pytest
from fastapi import status
from app.models import Movie, Certification, User


def test_cart_and_order_full_workflow(client, db_session):
    email = "buyer@example.com"
    password = "SecurePassword123!"

    client.post("/api/v1/auth/register", json={"email": email, "password": password})
    user = db_session.query(User).filter(User.email == email).first()
    user.is_active = True
    db_session.commit()

    login_res = client.post("/api/v1/auth/login", data={"username": email, "password": password})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    cert = Certification(name="PG-13_shopping")
    db_session.add(cert)
    db_session.commit()
    db_session.refresh(cert)

    movie = Movie(
        name="Inception for Sale", year=2010, time=148, imdb=8.8, votes=50000,
        description="Buy to watch", price=150.00, certification_id=cert.id
    )
    db_session.add(movie)
    db_session.commit()
    db_session.refresh(movie)

    res_get_cart = client.get("/api/v1/cart/", headers=headers)
    assert res_get_cart.status_code == status.HTTP_200_OK

    res_add_cart = client.post(f"/api/v1/cart/add/{movie.id}", headers=headers)
    assert res_add_cart.status_code == status.HTTP_201_CREATED

    res_create_order = client.post("/api/v1/orders/", headers=headers)
    assert res_create_order.status_code == status.HTTP_201_CREATED
    order_data = res_create_order.json()
    order_id = order_data["id"]

    res_order_details = client.get(f"/api/v1/orders/{order_id}", headers=headers)
    assert res_order_details.status_code == status.HTTP_200_OK
    assert res_order_details.json()["id"] == order_id

    res_my_orders = client.get("/api/v1/orders/", headers=headers)
    assert res_my_orders.status_code == status.HTTP_200_OK
    assert any(o["id"] == order_id for o in res_my_orders.json())

    res_cancel = client.patch(f"/api/v1/orders/{order_id}/cancel", headers=headers)
    assert res_cancel.status_code == status.HTTP_202_ACCEPTED


def test_remove_from_cart_success(client, db_session):
    email = "cart_cleaner@example.com"
    password = "SecurePassword123!"

    client.post("/api/v1/auth/register", json={"email": email, "password": password})
    user = db_session.query(User).filter(User.email == email).first()
    user.is_active = True
    db_session.commit()

    login_res = client.post("/api/v1/auth/login", data={"username": email, "password": password})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    cert = Certification(name="PG-13_cart_remove_unique")
    db_session.add(cert)
    db_session.commit()
    db_session.refresh(cert)

    movie = Movie(
        name="Disposable Movie", year=2020, time=90, imdb=5.0, votes=10,
        description="To be removed", price=10.00, certification_id=cert.id
    )
    db_session.add(movie)
    db_session.commit()
    db_session.refresh(movie)

    client.post(f"/api/v1/cart/add/{movie.id}", headers=headers)

    res_remove = client.delete(f"/api/v1/cart/remove/{movie.id}", headers=headers)
    assert res_remove.status_code == status.HTTP_200_OK
