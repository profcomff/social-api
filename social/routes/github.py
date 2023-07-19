import logging

from fastapi import APIRouter, BackgroundTasks, Request
from fastapi_sqlalchemy import db

from social.handlers_github import process_event
from social.models.webhook_storage import WebhookStorage, WebhookSystems
from social.settings import get_settings


router = APIRouter(prefix="/github", tags=["webhooks"])
settings = get_settings()
logger = logging.getLogger(__name__)


@router.post('')
async def github_webhook(request: Request, background_tasks: BackgroundTasks):
    """Принимает любой POST запрос от github"""
    request_data = await request.json()
    logger.debug(request_data)

    db.session.add(
        WebhookStorage(
            system=WebhookSystems.GITHUB,
            message=request_data,
        )
    )
    db.session.commit()

    background_tasks.add_task(process_event, request_data)

    return
