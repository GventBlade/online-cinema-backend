from typing import Optional

from fastapi import APIRouter, Header, HTTPException, Request, Depends
from app.core.config import settings
import stripe
from app.database import SessionLocal
from app.dependencies import get_current_user
from app.database import get_db
from sqlalchemy.orm import Session
from app.api.crud import order as order_crud
from app.models import OrderStatusEnum
from app.services.payment_service import PaymentService
from app.schemas.payments import PaymentResponse

router = APIRouter()

stripe.api_key = settings.STRIPE_SECRET_KEY


@router.post("/create-checkout-session/{order_id}")
async def create_checkout_session(
    order_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    order = order_crud.get_order_by_id(db, order_id=order_id, user_id=current_user.id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    session = await PaymentService.create_checkout_session(db, order, current_user.email)
    return {"checkout_url": session.url}


@router.post("/webhook")
async def stripe_webhook(request: Request, stripe_signature: str = Header(None)):
    payload = await request.body()

    try:
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, settings.STRIPE_WEBHOOK_SECRET
        )
    except (ValueError, stripe.error.SignatureVerificationError) as e:
        print(f"❌ Webhook signature verification failed: {e}")
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        try:
            metadata = session["metadata"]
            order_id = int(metadata["order_id"])
            user_id = int(metadata["user_id"])

            print(f"✅ Data received: Order {order_id}, User {user_id}")

            with SessionLocal() as db:
                order = order_crud.get_order_by_id(db, order_id=order_id, user_id=user_id)

                if order and order.status == OrderStatusEnum.PENDING:
                    from app.api.crud.payment import create_payment_record

                    create_payment_record(db, order, external_id=session.id)

                    order.status = OrderStatusEnum.PAID

                    db.commit()
                    print(f"✅ Order {order_id} and Payment record created successfully")
                else:
                    print(f"⚠️ Order {order_id} already processed or not found")

        except KeyError as e:
            print(f"❌ Error: Key {e} not found in Stripe metadata")
            return {"status": "error", "message": "Metadata missing"}
        except Exception as e:
            print(f"❌ Unexpected error during webhook processing: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

    return {"status": "success"}


@router.get("/my", response_model=list[PaymentResponse])
def my_payments(db: Session = Depends(get_db) ,current_user = Depends(get_current_user)):
    from app.api.crud.payment import get_user_payment_history
    return get_user_payment_history(db, user_id=current_user.id)


@router.get("/admin/all", response_model=list[PaymentResponse])
def get_all_payments_for_admin(
    status: Optional[str] = None,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    if current_user.group.name != "ADMIN":
        raise HTTPException(status_code=403, detail="Not enough permissions")

    from app.api.crud.payment import get_all_payments_admin
    return get_all_payments_admin(db, status=status, user_id=user_id)
