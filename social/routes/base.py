from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_sqlalchemy import DBSessionMiddleware

from social import __version__
from social.handlers_telegram import get_application as get_telegram
from social.settings import get_settings

from .discord import router as discord_router
from .github import router as github_router
from .telegram import router as telegram_router
from .vk import router as vk_router


settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    telegram = get_telegram()
    if telegram:
        await telegram.initialize()
        await telegram.start()
    yield
    if telegram:
        await telegram.stop()
        await telegram.shutdown()


app = FastAPI(
    title='Сервис мониторинга активности',
    description=('Серверная часть сервиса для выдачи печенек за активности'),
    version=__version__,
    lifespan=lifespan,
    # Настраиваем интернет документацию
    root_path=settings.ROOT_PATH if __version__ != 'dev' else '',
    docs_url=None if __version__ != 'dev' else '/docs',
    redoc_url=None,
)


app.add_middleware(
    DBSessionMiddleware,
    db_url=str(settings.DB_DSN),
    engine_args={"pool_pre_ping": True, "isolation_level": "AUTOCOMMIT"},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOW_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)


app.include_router(github_router)
app.include_router(telegram_router)
app.include_router(vk_router)
app.include_router(discord_router)
