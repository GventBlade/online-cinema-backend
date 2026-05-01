from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models import (
    User, UserGroup, UserGroupEnum, UserProfile,
    Movie, Certification, Order, OrderItem, OrderStatusEnum
)
from decimal import Decimal

# Створюємо таблиці, якщо їх ще немає
Base.metadata.create_all(bind=engine)


def seed_db():
    db = SessionLocal()
    try:
        # 1. Перевіряємо або створюємо групи
        admin_group = db.query(UserGroup).filter(UserGroup.name == UserGroupEnum.ADMIN).first()
        if not admin_group:
            admin_group = UserGroup(name=UserGroupEnum.ADMIN)
            db.add(admin_group)

        user_group = db.query(UserGroup).filter(UserGroup.name == UserGroupEnum.USER).first()
        if not user_group:
            user_group = UserGroup(name=UserGroupEnum.USER)
            db.add(user_group)

        db.flush()

        # 2. Шукаємо існуючого користувача або створюємо нового
        test_user = db.query(User).filter(User.email == "vanno@example.com").first()
        if not test_user:
            test_user = User(
                email="vanno@example.com",
                hashed_password="hashed_password_here",
                is_active=True,
                group_id=user_group.id
            )
            db.add(test_user)
            db.flush()

            profile = UserProfile(user_id=test_user.id, first_name="Vitalii", last_name="Prykhodko")
            db.add(profile)

        # 3. Створюємо НОВИЙ фільм (щоб не було конфліктів)
        cert = db.query(Certification).filter(Certification.name == "12+").first()
        if not cert:
            cert = Certification(name="12+")
            db.add(cert)
            db.flush()

        # Додаємо "Interstellar" замість "Inception"
        new_movie = Movie(
            name="MATRIX",
            year=2001,
            time=169,
            imdb=1.9,
            votes=1800000,
            description="A team of explorers travel through a wormhole in space...",
            price=Decimal("111.00"),
            certification_id=cert.id
        )
        db.add(new_movie)
        db.flush()

        # 4. Створюємо НОВЕ замовлення (Order #3 або наступне)
        # Сума 20.00 (як ціна фільму) або будь-яка інша для тесту
        new_order = Order(
            user_id=test_user.id,
            status=OrderStatusEnum.PENDING,
            total_amount=Decimal("20.00")
        )
        db.add(new_order)
        db.flush()

        order_item = OrderItem(
            order_id=new_order.id,
            movie_id=new_movie.id,
            price_at_order=Decimal("20.00")
        )
        db.add(order_item)

        db.commit()
        print(f"✅ Новий фільм додано! Movie: {new_movie.name}")
        print(f"✅ Створено нове замовлення ID: {new_order.id} на суму {new_order.total_amount}")

    except Exception as e:
        print(f"❌ Помилка під час сіду: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_db()