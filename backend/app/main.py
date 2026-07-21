from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth as auth_router

from app.routers import stocks
from app.routers import watchlist as watchlist_router

from app.routers import search_history

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

app.include_router(auth_router.router)

app.include_router(watchlist_router.router)

app.include_router(search_history.router)

@app.get("/")
def root():
    return {
        "message": "Welcome to AI Stock Market API"
    }