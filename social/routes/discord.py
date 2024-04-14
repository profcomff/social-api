import logging

from fastapi import APIRouter, BackgroundTasks, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi_sqlalchemy import db
from nacl.exceptions import BadSignatureError
from nacl.signing import VerifyKey

from social.handlers_discord.base import process_event
from social.models.webhook_storage import WebhookStorage, WebhookSystems
from social.settings import get_settings


router = APIRouter(prefix="/discord", tags=["webhooks"])
settings = get_settings()
logger = logging.getLogger(__name__)


@router.post('')
async def discord_webhook(request: Request, background_tasks: BackgroundTasks):
    """Принимает любой POST запрос от discord"""
    request_data: dict[str] = await request.json()
    logger.debug(request_data)

    signature = request.headers.get("X-Signature-Ed25519", "")
    timestamp = request.headers.get("X-Signature-Timestamp", "")
    body = (await request.body()).decode("utf-8")

    try:
        verify_key = VerifyKey(bytes.fromhex(settings.DISCORD_PUBLIC_KEY))
        verify_key.verify(f'{timestamp}{body}'.encode(), bytes.fromhex(signature))
    except BadSignatureError:
        raise HTTPException(401, 'invalid request signature')

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
