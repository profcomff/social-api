import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi_sqlalchemy import db

from social.settings import get_settings
from social.models.webhook_storage import WebhookStorage, WebhookSystems


router = APIRouter(prefix="/github", tags=["webhooks"])
settings = get_settings()
logger = logging.getLogger(__name__)


@router.post('')
async def github_webhook(request: Request):
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

    return
