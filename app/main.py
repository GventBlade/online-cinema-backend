from fastapi import FastAPI
from app.api.endpoints import auth  # Імпортуємо твій новий файл

app = FastAPI(title="Online Cinema API")

app.include_router(auth.router, prefix="/api/v1/auth")

@app.get("/")
def root():
    return {"message": "Welcome to Online Cinema API"}
