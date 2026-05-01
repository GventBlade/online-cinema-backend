import stripe
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models import Order

stripe.api_key = settings.STRIPE_SECRET_KEY

class PaymentService:
    @staticmethod
    async def create_checkout_session(db: Session, order: Order, user_email: str):
        actual_total = sum(item.price_at_order for item in order.items)

        if actual_total != order.total_amount:
            order.total_amount = actual_total
            db.add(order)
            db.commit()
            db.refresh(order)

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': f'Order #{order.id}',
                        'description': f'Payment for movies in order #{order.id}',
                    },
                    'unit_amount': int(order.total_amount * 100),
                },
                'quantity': 1,
            }],
            mode='payment',
            metadata={
                "order_id": str(order.id),
                "user_id": str(order.user_id)
            },
            success_url=settings.STRIPE_SUCCESS_URL,
            cancel_url=settings.STRIPE_CANCEL_URL,
            customer_email=user_email,
        )
        return session
