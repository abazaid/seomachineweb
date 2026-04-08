from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import auth, connections, content, health, publishing, reports, settings, tasks
from app.core.config import get_settings
from app.core.db import Base, SessionLocal, engine
from app.core.security import get_password_hash
from app import models  # noqa: F401
from app.models.user import User


app_settings = get_settings()

app = FastAPI(title=app_settings.app_name)

_raw_origins = [origin.strip() for origin in app_settings.backend_cors_origins.split(',') if origin.strip()]
_allow_all = '*' in _raw_origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'] if _allow_all else _raw_origins,
    allow_credentials=not _allow_all,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.on_event('startup')
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        existing_admin = db.query(User).filter(User.email == 'admin@zerovape.com').first()
        if not existing_admin:
            db.add(
                User(
                    email='admin@zerovape.com',
                    full_name='Platform Admin',
                    hashed_password=get_password_hash('Admin@12345'),
                    role='admin',
                )
            )
            db.commit()
    finally:
        db.close()


app.include_router(health.router)
app.include_router(auth.router, prefix=app_settings.api_v1_prefix)
app.include_router(settings.router, prefix=app_settings.api_v1_prefix)
app.include_router(connections.router, prefix=app_settings.api_v1_prefix)
app.include_router(reports.router, prefix=app_settings.api_v1_prefix)
app.include_router(tasks.router, prefix=app_settings.api_v1_prefix)
app.include_router(content.router, prefix=app_settings.api_v1_prefix)
app.include_router(publishing.router, prefix=app_settings.api_v1_prefix)
