from datetime import date
from typing import Optional, List
import stripe
import traceback

from fastapi import APIRouter, Header, HTTPException, Request, Depends, BackgroundTasks
from sqlalchemy.orm import Session, joinedload

from app.core.config import settings
from app.database import SessionLocal, get_db
from app.dependencies import get_current_user
from app.models import Order, OrderStatusEnum, PaymentStatus, Payment, PaymentItem
from app.services.payment_service import PaymentService
from app.services.email_service import EmailService
from app.schemas.payments import PaymentResponse
from app.api.crud import order as order_crud
from app.api.crud.payment import create_payment_record, get_user_payment_history, get_all_payments_admin

router = APIRouter()

stripe.api_key = settings.STRIPE_SECRET_KEY


@router.post("/create-checkout-session/{order_id}")
async def create_checkout_session(
    order_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    order = order_crud.get_order_by_id(db, order_id=order_id, user_id=current_user.id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    session = await PaymentService.create_checkout_session(db, order, current_user.email)
    return {"checkout_url": session.url}


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    stripe_signature: str = Header(None)
):
    payload = await request.body()

    try:
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, settings.STRIPE_WEBHOOK_SECRET
        )
    except (ValueError, stripe.error.SignatureVerificationError) as e:
        print(f"⚠️ Webhook signature verification failed: {e}")
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    print(f"📡 Received Stripe event: {event['type']}")

    event_data = event.to_dict()
    data_object = event_data.get('data', {}).get('object', {})

    if event['type'] == 'checkout.session.completed':
        session_id = data_object.get('id')
        print(f"🔔 Processing checkout.session.completed: {session_id}")

        try:
            metadata = data_object.get('metadata', {})
            order_id = metadata.get('order_id')

            if not order_id:
                print("❌ Error: order_id is missing in metadata!")
                return {"status": "error", "message": "No order_id"}

            with SessionLocal() as db:
                order = db.query(Order).options(
                    joinedload(Order.user),
                    joinedload(Order.items)
                ).filter(Order.id == int(order_id)).first()

                if order and order.status == OrderStatusEnum.PENDING:
                    payment_intent = data_object.get('payment_intent')

                    payment_record = create_payment_record(db, order, external_id=payment_intent)

                    for item in order.items:
                        new_payment_item = PaymentItem(
                            payment_id=payment_record.id,
                            order_item_id=item.id,
                            price_at_payment=item.price_at_order
                        )
                        db.add(new_payment_item)

                    order.status = OrderStatusEnum.PAID
                    db.commit()
                    print(f"📝 Database updated: Order #{order.id} is now PAID with item breakdown")

                    if order.user and order.user.email:
                        background_tasks.add_task(
                            EmailService.send_payment_confirmation,
                            user_email=order.user.email,
                            order_id=order.id,
                            amount=float(order.total_amount)
                        )
                else:
                    status = order.status if order else "NOT FOUND"
                    print(f"ℹ️ Skipping: Order status is {status}")

        except Exception as e:
            print(f"🔥 Error during payment success logic: {str(e)}")
            traceback.print_exc()
            return {"status": "error", "message": str(e)}

    elif event['type'] == 'charge.refunded':
        payment_intent_id = data_object.get('payment_intent')
        print(f"🔄 Processing refund for PaymentIntent: {payment_intent_id}")

        if payment_intent_id:
            with SessionLocal() as db:
                payment = db.query(Payment).options(
                    joinedload(Payment.order).joinedload(Order.user)
                ).filter(Payment.external_payment_id == payment_intent_id).first()

                if payment:
                    payment.status = PaymentStatus.REFUNDED

                    if payment.order:
                        payment.order.status = OrderStatusEnum.CANCELED
                        order_id = payment.order.id
                        total_amount = float(payment.order.total_amount)
                        user_email = payment.order.user.email if payment.order.user else None

                        print(f"🚫 Order #{order_id} set to CANCELED. Sending email...")

                        if user_email:
                            background_tasks.add_task(
                                EmailService.send_refund_notification,
                                user_email=user_email,
                                order_id=order_id,
                                amount=total_amount
                            )

                    db.commit()
                    print("📝 Database updated: Refund processed successfully")
                else:
                    print(f"⚠️ Payment record {payment_intent_id} not found in DB")

    return {"status": "success"}


@router.get("/admin/all", response_model=List[PaymentResponse])
def get_all_payments_for_admin(
    status: Optional[str] = None,
    user_id: Optional[int] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.group.name != "ADMIN":
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return get_all_payments_admin(
        db,
        status=status,
        user_id=user_id,
        date_from=date_from,
        date_to=date_to
    )


@router.get("/success")
def payment_success():
    return {"status": "success", "message": "Payment successful! Thank you for your purchase."}

@router.get("/cancel")
def payment_cancel():
    return {"status": "canceled", "message": "Payment was cancelled."}


@router.get("/my", response_model=List[PaymentResponse])
def get_my_payment_history(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
        User can view the history of all their payments: Date, Amount, Status.
        """
    return get_user_payment_history(db, user_id=current_user.id)
