import logging
import random
import string

from auth_lib.fastapi import UnionAuth
from fastapi import APIRouter, Depends, Request
from fastapi.responses import PlainTextResponse
from fastapi_sqlalchemy import db
from pydantic import BaseModel, ConfigDict

from social.handlers_telegram import get_application
from social.models.vk import VkGroups
from social.models.webhook_storage import WebhookStorage, WebhookSystems
from social.settings import get_settings


router = APIRouter(prefix="/vk", tags=['vk'])
settings = get_settings()
logger = logging.getLogger(__name__)
application = get_application()


class VkGroupCreate(BaseModel):
    confirmation_token: str
    change_secret_key: bool = False


class VkGroupCreateResponse(BaseModel):
    group_id: int
    secret_key: str

    model_config = ConfigDict(from_attributes=True)


@router.post('', tags=["webhooks"])
async def vk_webhook(request: Request):
    """Принимает любой POST запрос от Telegram"""
    request_data = await request.json()
    logger.debug(request_data)
    group_id = request_data["group_id"]  # Fail if no group
    group = db.session.query(VkGroups).where(VkGroups.group_id == group_id).one()  # Fail if no settings

    # Проверка на создание нового вебхука со страничка ВК
    if request_data.get("type", "") == "confirmation":
        return PlainTextResponse(group.confirmation_token)

    if request_data.get("secret") != group.secret_key:
        raise Exception("Not a valid secret")

    db.session.add(
        WebhookStorage(
            system=WebhookSystems.VK,
            message=request_data,
        )
    )
    db.session.commit()

    return


def random_string(N: int):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=N))


@router.put('/{group_id}')
def create_or_replace_group(
    group_id: int, group_info: VkGroupCreate, _=Depends(UnionAuth(["social.vk_group.create"]))
) -> VkGroupCreateResponse:
    group = db.session.query(VkGroups).where(VkGroups.group_id == group_id).one_or_none()
    if group is None:
        group = VkGroups()
        db.session.add(group)
        group.group_id = group_id
        group.secret_key = random_string(32)

    if group_info.change_secret_key:
        group.secret_key = random_string(32)

    group.confirmation_token = group_info.confirmation_token

    db.session.commit()
    return group
