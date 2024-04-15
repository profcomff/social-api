from datetime import UTC, datetime
from social.models import TelegramChannel, TelegramChat, CreateGroupRequest

from fastapi_sqlalchemy import db
from telegram import Update


def create_telegram_group(update: Update):
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
    group = create_telegram_group(update)
    text = update.effective_message.text
    if not text or not group:
        return
    text = text.removeprefix('/validate').removeprefix('@ViribusSocialBot').strip()
    db.session.query(CreateGroupRequest).where(CreateGroupRequest.secret_key == text).update(
        {CreateGroupRequest.mapped_group_id: group.id}
    )