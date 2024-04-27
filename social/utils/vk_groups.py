import logging
from datetime import UTC, datetime

import requests
from fastapi_sqlalchemy import db

from social.models import CreateGroupRequest, VkChat
from social.settings import get_settings


logger = logging.getLogger(__name__)
settings = get_settings()


def get_chat_name(peer_id):
    """Получить название чата ВК"""
    conversation = requests.post(
        "https://api.vk.com/method/messages.getConversationsById",
        json={
            "peer_ids": peer_id,
            "group_id": settings.VK_BOT_GROUP_ID,
            "access_token": settings.VK_BOT_TOKEN,
            "v": 5.199,
        },
    )
    try:
        return conversation["response"]["items"][0]["chat_settings"]["title"]
    except Exception as exc:
        logger.exception(exc)
        return None


def create_vk_chat(request_data: dict[str]):
    """Создает запись о вк чате в внутренней БД приложения или возвращает существующий"""
    if (
        request_data.get("group_id") == settings.VK_BOT_GROUP_ID  # peer_id чатов уникальные для каждого пользователя ВК
        and request_data.get("type") == "message_new"
    ):
        # Получение сообщения в чате ВК
        try:
            peer_id = request_data["object"]["message"]["peer_id"]
            obj = db.session.query(VkChat).where(VkChat.peer_id == peer_id).one_or_none()
            if obj is None:
                obj = VkChat(peer_id=peer_id)
                db.session.add(obj)
            obj.last_active_ts = datetime.now(UTC)
            db.session.commit()
        except Exception as exc:
            logger.exception(exc)
        return obj
    return None


def approve_vk_chat(request_data: dict[str]):
    """Если получено сообщение команды /validate, то за группой закрепляется владелец"""
    logger.debug("Validation started")
    group = create_vk_chat(request_data)
    text = request_data.get("object", {}).get("message", {}).get("text", "").removeprefix("/validate").strip()
    if not text or not group or group.owner_id is not None:
        logger.error("Telegram group not validated (secret=%s, group=%s)", text, group)
        return
    request = db.session.query(CreateGroupRequest).where(CreateGroupRequest.secret_key == text).one_or_none()
    request.mapped_group_id = group.id
    group.owner_id = request.owner_id
    db.session.commit()
    logger.info("VK group %d validated (secret=%s)", group.id, text)
