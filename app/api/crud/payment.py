from sqlalchemy.orm import Session, joinedload
from datetime import date, datetime, time
from app.models import Payment, PaymentItem, PaymentStatus, Order, User

def create_payment_record(db: Session, order: Order, external_id: str):
    new_payment = Payment(
        user_id=order.user_id,
        order_id=order.id,
        amount=order.total_amount,
        status=PaymentStatus.SUCCESSFUL,
        external_payment_id=external_id
    )
    db.add(new_payment)
    db.flush()
    for order_item in order.items:
        payment_item = PaymentItem(
            payment_id=new_payment.id,
            order_item_id=order_item.id,
            price_at_payment = order_item.price_at_order
        )
        db.add(payment_item)

    return new_payment


def get_user_payment_history(db: Session, user_id: int):
    return db.query(Payment
                    ).options(joinedload(Payment.items).joinedload(PaymentItem.order_item)
                              ).filter(Payment.user_id == user_id).order_by(Payment.created_at.desc()).all()


def get_all_payments_admin(
    db: Session,
    status: str = None,
    user_id: int = None,
    date_from: date = None,
    date_to: date = None
):
    query = db.query(Payment).options(joinedload(Payment.user))

    if status:
        query = query.filter(Payment.status == status)

    if user_id:
        query = query.filter(Payment.user_id == user_id)

    if date_from:
        dt_from = datetime.combine(date_from, time.min)
        query = query.filter(Payment.created_at >= dt_from)

    if date_to:
        dt_to = datetime.combine(date_to, time.max)
        query = query.filter(Payment.created_at <= dt_to)

    return query.order_by(Payment.created_at.desc()).all()
