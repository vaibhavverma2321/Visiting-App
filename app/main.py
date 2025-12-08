from fastapi import FastAPI
from database import engine, Base
from routes import users, cards

app = FastAPI(title="Visiting Card API")

Base.metadata.create_all(bind=engine)

app.include_router(users.router)
app.include_router(cards.router)
