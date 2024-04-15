import logging
from asyncio import create_task

from fastapi import APIRouter, Request
from fastapi_sqlalchemy import db
from telegram import Update

from social.handlers_telegram import get_application
from social.models.webhook_storage import WebhookStorage, WebhookSystems
from social.settings import get_settings
from social.utils.telegram_groups import create_telegram_group


router = APIRouter(prefix="/telegram", tags=["webhooks"])
settings = get_settings()
logger = logging.getLogger(__name__)
application = get_application()


@router.post('')
async def telegram_webhook(request: Request):
    """Принимает любой POST запрос от Telegram"""
    request_data = await request.json()
    logger.debug(request_data)

    db.session.add(
        WebhookStorage(
            system=WebhookSystems.TELEGRAM,
            message=request_data,
        )
    )
    db.session.commit()

    update = Update.de_json(data=request_data, bot=application.bot)
    await application.update_queue.put(update)
    try:
        create_telegram_group(update)
    except Exception as exc:
        logger.exception(exc)
