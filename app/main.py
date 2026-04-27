from fastapi import FastAPI
from app.api.endpoints import auth, movies, interactions, cart, orders

app = FastAPI(title="Online Cinema API")

app.include_router(auth.router, prefix="/api/v1/auth")
app.include_router(movies.router, prefix="/api/v1/movies")
app.include_router(interactions.router, prefix="/api/v1/movies")
app.include_router(cart.router, prefix="/api/v1/cart", tags=["Cart"])
app.include_router(orders.router, prefix="/api/v1/orders", tags=["Orders"])

@app.get("/")
def root():
    return {"message": "Welcome to Online Cinema API"}
