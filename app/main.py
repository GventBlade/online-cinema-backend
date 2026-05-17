import secrets
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi

from app.api.endpoints import auth, movies, interactions, cart, orders, payments
from app.core.config import settings


app = FastAPI(
    title="Online Cinema API",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

security = HTTPBasic()

def authenticate_swagger(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, settings.SWAGGER_USER)
    correct_password = secrets.compare_digest(credentials.password, settings.SWAGGER_PASSWORD)

    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

@app.get("/docs", include_in_schema=False)
async def overridden_swagger_id(username: str = Depends(authenticate_swagger)):
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title=app.title + " - Swagger UI"
    )

@app.get("/redoc", include_in_schema=False)
async def overridden_redoc_id(username: str = Depends(authenticate_swagger)):
    return get_redoc_html(
        openapi_url="/openapi.json",
        title=app.title + " - ReDoc"
    )

@app.get("/openapi.json", include_in_schema=False)
async def get_open_api_endpoint(username: str = Depends(authenticate_swagger)):
    return get_openapi(
        title=app.title,
        version="0.1.0",
        routes=app.routes,
    )

app.include_router(auth.router, prefix="/api/v1/auth")
app.include_router(movies.router, prefix="/api/v1/movies")
app.include_router(interactions.router, prefix="/api/v1/movies")
app.include_router(cart.router, prefix="/api/v1/cart", tags=["Cart"])
app.include_router(orders.router, prefix="/api/v1/orders", tags=["Orders"])
app.include_router(payments.router, prefix="/api/v1/payments", tags=["Payments"])
@app.get("/")
def root():
    return {"message": "Welcome to Online Cinema API"}
