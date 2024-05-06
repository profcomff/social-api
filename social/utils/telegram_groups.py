import logging
from datetime import UTC, datetime

import requests
from fastapi_sqlalchemy import db
from telegram import Update

from social.models import CreateGroupRequest, TelegramChannel, TelegramChat
from social.settings import get_settings


logger = logging.getLogger(__name__)
settings = get_settings()


def get_chat_info(id: int) -> dict:
    return requests.post(
        f'https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/getChat',
        json={'chat_id': id},
    ).json()


def create_telegram_group(update: Update):
    """Создает запись о телеграмм группе в внутренней БД приложения или возвращает существующий"""
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

    if not obj:
        return

    obj.last_active_ts = datetime.now(UTC)
    db.session.commit()
    return obj


def approve_telegram_group(update: Update):
    """Если получено сообщение команды /validate, то за группой закрепляется владелец"""
    logger.debug("Validation started")
    group = create_telegram_group(update)
    text = update.effective_message.text
    if not text or not group or group.owner_id is not None:
        logger.error("Telegram group not validated (secret=%s, group=%s)", text, group)
        return
    text = text.removeprefix('/validate').removeprefix('@ViribusSocialBot').strip()
    request = db.session.query(CreateGroupRequest).where(CreateGroupRequest.secret_key == text).one_or_none()
    request.mapped_group_id = group.id
    group.owner_id = request.owner_id
    db.session.commit()
    logger.info("Telegram group %d validated (secret=%s)", group.id, text)


def update_tg_chat(group: TelegramChat):
    chat_info = get_chat_info(group.chat_id)
    group.name = chat_info.get("title")
    group.description = chat_info.get("description")
    group.invite_link = chat_info.get("invite_link")
