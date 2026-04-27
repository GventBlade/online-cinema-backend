import stripe
from app.core.config import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

class PaymentService:
    @staticmethod
    async def create_checkout_session(db, order, user_email: str):
        session = None
        try:
            amount_in_cents = int(order.total_amount * 100)

            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': f"Оплата замовлення #{order.id}",
                        },
                        'unit_amount': amount_in_cents,
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url="http://127.0.0.1:8000/docs",
                cancel_url="http://127.0.0.1:8000/docs",
                customer_email=user_email,
                metadata={
                    "order_id": order.id,
                    "user_id": order.user_id
                }
            )
        except Exception as e:
            print(f"❌ Stripe Error: {str(e)}")
            from fastapi import HTTPException
            raise HTTPException(status_code=400, detail=f"Stripe error: {str(e)}")

        return session