import logging
from datetime import UTC, datetime

from auth_lib.fastapi import UnionAuth
from fastapi import APIRouter, Depends
from fastapi_sqlalchemy import db
from pydantic import BaseModel

from social.exceptions import GroupRequestNotFound
from social.models.create_group_request import CreateGroupRequest
from social.settings import get_settings


router = APIRouter(prefix="/group", tags=['User defined groups'])
settings = get_settings()
logger = logging.getLogger(__name__)


class GroupRequestGet(BaseModel):
    secret_key: str
    valid_ts: datetime


class GroupGet(BaseModel):
    id: int


@router.post('')
def create_group_request(
    user: dict[str] = Depends(UnionAuth(["social.group.create"])),
) -> GroupRequestGet:
    obj = CreateGroupRequest(owner_id=user.get("id"))
    db.session.add(obj)
    db.session.commit()
    return obj


@router.get('')
def validate_group_request(
    secret_key: str,
    user: dict[str] = Depends(UnionAuth(["social.group.create"])),
) -> GroupGet | GroupRequestGet:
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
