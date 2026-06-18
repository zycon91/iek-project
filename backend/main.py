from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from db.database import Base, engine
from routers import users_router, movies_router, payments_router, purchases_router, rentals_router, subscriptions_router, checkout_router
from utils.storage import UPLOAD_DIR

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=UPLOAD_DIR), name="static")

app.include_router(users_router)
app.include_router(movies_router)
app.include_router(payments_router)
app.include_router(purchases_router)
app.include_router(rentals_router)
app.include_router(subscriptions_router)
app.include_router(checkout_router)