import logging
from asyncio import create_task
from datetime import UTC, datetime

from fastapi import APIRouter, Request
from fastapi_sqlalchemy import db
from telegram import Update

from social.handlers_telegram import get_application
from social.models import TelegramChannel, TelegramChat
from social.models.webhook_storage import WebhookStorage, WebhookSystems
from social.settings import get_settings


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
    add_msg = create_task(application.update_queue.put(update))
    try:
        chat = update.effective_chat
        obj = None
        if chat.type in ['group', 'supergroup']:
            obj = db.session.query(TelegramChat).where(TelegramChat.chat_id == chat.id).one_or_none()
            if obj is None:
                obj = TelegramChat(chat_id=chat.id)
                db.session.add(obj)
        elif chat.type == 'channel':
            obj = db.session.query(TelegramChannel).where(TelegramChannel.channel_id == chat.id).one_or_none()
            if obj is None:
                obj = TelegramChannel(channel_id=chat.id)
                db.session.add(obj)

        obj.last_active_ts = datetime.now(UTC)
        db.session.commit()
        logger.debug(obj)
    except Exception as exc:
        logger.exception(exc)
    finally:
        await add_msg

    return
