from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_sqlalchemy import DBSessionMiddleware

from social import __version__
from social.handlers_telegram import get_application as get_telegram
from social.settings import get_settings

from .github import router as github_router
from .telegram import router as telegram_router
from .vk import router as vk_router
from .discord import router as discord_router


settings = get_settings()
app = FastAPI(
    title='Сервис мониторинга активности',
    description=('Серверная часть сервиса для выдачи печенек за активности'),
    version=__version__,
    # Настраиваем интернет документацию
    root_path=settings.ROOT_PATH if __version__ != 'dev' else '/',
    docs_url=None if __version__ != 'dev' else '/docs',
    redoc_url=None,
)
telegram = get_telegram()


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


@app.on_event("startup")
async def startup():
    await telegram.initialize()
    await telegram.start()


@app.on_event("shutdown")
async def shutdown():
    await telegram.stop()
    await telegram.shutdown()


app.include_router(github_router)
app.include_router(telegram_router)
app.include_router(vk_router)
app.include_router(discord_router)
