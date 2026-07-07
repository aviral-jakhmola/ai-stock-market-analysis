from fastapi import FastAPI
from app.routers import stocks

app = FastAPI(
    title="AI Stock Market API",
    version="1.0.0"
)

app.include_router(stocks.router)

@app.get("/")
def root():
    return {
        "message": "Welcome to AI Stock Market API"
    }