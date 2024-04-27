import logging

from auth_lib.fastapi import UnionAuth
from fastapi import APIRouter, BackgroundTasks, Depends, Request
from fastapi.responses import PlainTextResponse
from fastapi_sqlalchemy import db
from pydantic import BaseModel, ConfigDict

from social.handlers_vk.base import process_event
from social.models.group import VkGroup
from social.models.webhook_storage import WebhookStorage, WebhookSystems
from social.settings import get_settings
from social.utils.string import random_string
from social.utils.vk_groups import create_vk_chat


router = APIRouter(prefix="/vk", tags=['vk'])
settings = get_settings()
logger = logging.getLogger(__name__)


class VkGroupCreate(BaseModel):
    confirmation_token: str
    change_secret_key: bool = False


class VkGroupCreateResponse(BaseModel):
    group_id: int
    secret_key: str

    model_config = ConfigDict(from_attributes=True)


@router.post('', tags=["webhooks"])
async def vk_webhook(request: Request, background_tasks: BackgroundTasks) -> str:
    """Принимает любой POST запрос от VK"""
    request_data = await request.json()
    logger.debug(request_data)
    group_id = request_data["group_id"]  # Fail if no group
    group = db.session.query(VkGroup).where(VkGroup.group_id == group_id).one()  # Fail if no settings

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

    background_tasks.add_task(create_vk_chat, request_data)
    background_tasks.add_task(process_event, request_data)
    return PlainTextResponse('ok')


@router.put('/{group_id}')
def create_or_replace_group(
    group_id: int,
    group_info: VkGroupCreate,
    user: dict[str] = Depends(UnionAuth(["social.group.create"])),
) -> VkGroupCreateResponse:
    group = db.session.query(VkGroup).where(VkGroup.group_id == group_id).one_or_none()
    if group is None:
        group = VkGroup()
        group.owner_id = user.get("id")
        db.session.add(group)
        group.group_id = group_id
        group.secret_key = random_string(32)

    if group_info.change_secret_key:
        group.secret_key = random_string(32)

    group.confirmation_token = group_info.confirmation_token

    db.session.commit()
    return group
