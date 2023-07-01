"""Работа с чатом Viribus Unitis https://t.me/ViribusUnitisGroup

Для создания нового обработчика создай асинхронную функцию в конце файла с параметрами
Update и Context, а потом зарегистрируй ее внутри функции `register_handlers`.
"""
import logging
from textwrap import dedent
from random import choice

from telegram import Update
from telegram.ext import (
    Application,
    MessageHandler,
    ContextTypes,
)
from telegram.ext.filters import (Chat)

from social.settings import get_settings


logger = logging.getLogger(__name__)
settings = get_settings()

CHAT_ID = -1001758480664
MAIN_TOPIC_ID = 55106

GREETINGS = [
    """
    Привет, [{name}](tg://user?id={id}), и добро пожаловать в наш клуб!

    Расскажи, что привело тебя к нам и откуда о нас узнал?
    """
]

def register_handlers(app: Application):
    app.add_handler(MessageHandler(Chat(CHAT_ID), delete_system_message))
    logger.info("Viribus Unitis handlers activated")


async def delete_system_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for user in update.message.new_chat_members:
        await context.bot.send_message(
            chat_id=CHAT_ID,
            message_thread_id=MAIN_TOPIC_ID,
            text=dedent(choice(GREETINGS)).format(
                name=user.name, id=user.id
            ),
            parse_mode='markdown',
        )
        logger.info(f"User {user.name} greeting sent")

    if update.message.message_thread_id is None:
        logger.info(f"Message from general channel handled")
        await update.message.delete()
