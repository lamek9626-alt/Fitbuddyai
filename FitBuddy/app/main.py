from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .config import BASE_DIR, get_settings
from .database import init_db
from .routes import router

@asynccontextmanager
async def lifespan(app):
    init_db()
    yield

settings=get_settings()
app=FastAPI(title=settings.app_name,description="AI-powered 7-day workout and wellness plan generator.",version="1.0.0",lifespan=lifespan)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
app.include_router(router)
