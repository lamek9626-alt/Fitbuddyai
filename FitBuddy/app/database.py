from collections.abc import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import StaticPool
from .config import get_settings

class Base(DeclarativeBase):
    pass

settings = get_settings()
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
pool_args = {"poolclass": StaticPool} if settings.database_url in {"sqlite://", "sqlite:///:memory:"} else {}
engine = create_engine(settings.database_url, connect_args=connect_args, future=True, **pool_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)

def init_db() -> None:
    from .models import User, Plan
    Base.metadata.create_all(bind=engine)

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
