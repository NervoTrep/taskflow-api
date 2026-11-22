"""FastAPI application factory."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import models  # noqa: F401 - register tables with Base.metadata
from app.db import Base, engine
from app.routers.tasks import router as tasks_router


def create_app(*, init_db: bool = True) -> FastAPI:
    @asynccontextmanager
    async def lifespan(application: FastAPI):
        # Suitable for a learning project. For production use Alembic migrations.
        if init_db:
            Base.metadata.create_all(bind=engine)
        yield

    application = FastAPI(
        title="TaskFlow API",
        description="A REST API for managing tasks, built with FastAPI and SQLAlchemy.",
        version="1.0.0",
        lifespan=lifespan,
    )
    application.include_router(tasks_router)

    @application.get("/health", tags=["system"])
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return application


app = create_app()
