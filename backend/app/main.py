from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import stocks

app = FastAPI(
    title="AI Stock Market API",
    version="1.0.0"
)

# Allow the React dev server to talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(stocks.router)


@app.get("/")
def root():
    return {
        "message": "Welcome to AI Stock Market API"
    }