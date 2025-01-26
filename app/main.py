from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import (
    auth,
    market,
    wallet,
    trade,
    money
)
from .database import engine, Base
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="BO App API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(auth.router)
app.include_router(market.router)
app.include_router(wallet.router)
app.include_router(trade.router)
app.include_router(money.router)