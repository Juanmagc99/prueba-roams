from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.clients import clients_router
from app.core.database import create_db_and_tables, drop_all


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield
    drop_all()

app = FastAPI(lifespan=lifespan)

app.include_router(clients_router, prefix="/api", tags=["Clients"])
