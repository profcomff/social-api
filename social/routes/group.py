import logging
from datetime import UTC, datetime

from auth_lib.fastapi import UnionAuth
from fastapi import APIRouter, Depends
from fastapi_sqlalchemy import db
from pydantic import BaseModel

from social.exceptions import GroupNotFound, GroupRequestNotFound
from social.models.create_group_request import CreateGroupRequest
from social.models.group import Group
from social.settings import get_settings
from social.utils.telegram_groups import update_tg_chat
from social.utils.vk_groups import update_vk_chat, update_vk_group


router = APIRouter(prefix="/group", tags=['User defined groups'])
settings = get_settings()
logger = logging.getLogger(__name__)


class GroupRequestGet(BaseModel):
    secret_key: str
    valid_ts: datetime


class GroupGet(BaseModel):
    id: int
    owner_id: int | None = None
    name: str | None = None
    type: str | None = None
    description: str | None = None
    invite_link: str | None = None


class GroupGetMany(BaseModel):
    items: list[GroupGet]


class GroupPatch(BaseModel):
    update_from_source: bool | None = False
    name: str | None = None
    description: str | None = None
    invite_link: str | None = None


@router.post('')
def create_group_request(
    user: dict[str] = Depends(UnionAuth(["social.group.create"])),
) -> GroupRequestGet:
    obj = CreateGroupRequest(owner_id=user.get("id"))
    db.session.add(obj)
    db.session.commit()
    return obj


@router.get('/validation')
def validate_group_request(
    secret_key: str,
    user: dict[str] = Depends(UnionAuth(["social.group.create"])),
) -> GroupGet | GroupRequestGet:
    """Получение состояния валидации группы по коду валидации

    Трубуются права: `social.group.create`
    """
    obj = (
        db.session.query(CreateGroupRequest)
        .where(CreateGroupRequest.secret_key == secret_key, CreateGroupRequest.owner_id == user.get("id"))
        .one_or_none()
    )
    if obj is None or obj.valid_ts.replace(tzinfo=UTC) < datetime.now(UTC):
        raise GroupRequestNotFound(user_id=user.get("id"), secret_key=secret_key)

    if obj.mapped_group_id is not None:
        return GroupGet.model_validate(obj.mapped_group, from_attributes=True)

    return GroupRequestGet.model_validate(obj, from_attributes=True)


@router.get('')
def get_all_groups(
    my: bool = True,
    user: dict[str] = Depends(UnionAuth(allow_none=True, auto_error=False)),
) -> GroupGetMany:
    """Получение списка групп

    Трубуются права:
    - Для получения списка своих групп права не требуются (`my=True`)
    - `social.group.read` для чтения списка всех групп, подключенных к приложению
    """
    if not user:
        # Возвращаем список видимых всем групп
        return {"items": db.session.query(Group).where(Group.hidden == False).all()}

    if user and my:
        # Возвращаем только свои группы
        return {"items": db.session.query(Group).where(Group.owner_id == user.get("id")).all()}

    # Если у пользователя есть права на просмотр всех групп – показываем все неудаленные группы
    for scope in user.get("session_scopes", []):
        if scope.get("name") == "social.group.read":
            return {"items": db.session.query(Group).where(Group.is_deleted == False).all()}

    # Возвращаем пустный список если не прошли ни по одному условию
    logger.debug("User %s has no rights to get groups", user.get("id") if user else None)
    return {"items": []}


@router.patch('/{group_id}')
def update_group_info(
    group_id: int,
    patch_info: GroupPatch,
    user: dict[str] = Depends(UnionAuth()),
):
    group = db.session.get(Group, group_id)
    if group.owner_id != user.get("id"):
        raise GroupNotFound(user_id=user.get("id"), group_id=group_id)

    # Пытаемся получить данные из источника (получение название чата ВК/Telegram)
    if patch_info.update_from_source:
        if group.type == "vk_chat":
            update_vk_chat(group)
        elif group.type == "vk_group":
            update_vk_group(group)
        elif group.type == "tg_chat" or group.type == "tg_channel":
            update_tg_chat(group)

    # Ручное обновление данных
    if patch_info.name:
        group.name = patch_info.name
    if patch_info.description:
        group.description = patch_info.description
    if patch_info.invite_link:
        group.invite_link = patch_info.invite_link

    db.session.commit()
    return GroupGet.model_validate(group, from_attributes=True)
