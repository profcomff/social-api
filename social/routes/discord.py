import logging

from fastapi import APIRouter, BackgroundTasks, Request
from fastapi.responses import JSONResponse
from fastapi_sqlalchemy import db

from social.handlers_discord.base import process_event
from social.models.webhook_storage import WebhookStorage, WebhookSystems
from social.settings import get_settings


router = APIRouter(prefix="/discord", tags=["webhooks"])
settings = get_settings()
logger = logging.getLogger(__name__)


@router.post('')
async def discord_webhook(request: Request, background_tasks: BackgroundTasks):
    """Принимает любой POST запрос от discord"""
    request_data = await request.json()
    logger.debug(request_data)

    db.session.add(
        WebhookStorage(
            system=WebhookSystems.DISCORD,
            message=request_data,
        )
    )
    db.session.commit()

    if request_data.get("type") == 1:
        return JSONResponse({"type": 1})

    background_tasks.add_task(process_event, request_data)

    return
