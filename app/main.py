import os
from fastapi import FastAPI
from database import engine, Base
from routes import users, cards
from dotenv import load_dotenv
import uvicorn

load_dotenv()

app = FastAPI(title="Visiting Card API")

Base.metadata.create_all(bind=engine)

app.include_router(users.router)
app.include_router(cards.router)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
