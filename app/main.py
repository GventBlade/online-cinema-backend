from fastapi import FastAPI
from app.api.endpoints import auth, movies  # Імпортуємо твій новий файл

app = FastAPI(title="Online Cinema API")

app.include_router(auth.router, prefix="/api/v1/auth")
app.include_router(movies.router, prefix="/api/v1/movies")
@app.get("/")
def root():
    return {"message": "Welcome to Online Cinema API"}
