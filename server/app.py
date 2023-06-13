from fastapi import FastAPI
from .database import init_db
from .routes.login import router as router_login
app = FastAPI()
app.include_router(router_login, tags=["login"])


@app.on_event("startup")
async def start_db():
    await init_db()
    print('running app.....')


@app.get("/", tags=["Root"])
async def read_root() -> dict:
    return {"message": "Welcome to your beanie powered app!"}

