"""Работа с чатом Viribus Unitis https://t.me/ViribusUnitisGroup

Для создания нового обработчика создай асинхронную функцию в конце файла с параметрами
Update и Context, а потом зарегистрируй ее внутри функции `register_handlers`.
"""
from textwrap import dedent
from random import choice

from telegram import Update
from telegram.ext import (
    Application,
    ChatJoinRequestHandler,
    MessageHandler,
    ContextTypes,
)
from telegram.ext.filters import (Chat)

CHAT_ID = -1001758480664
MAIN_TOPIC_ID = 55106

def register_handlers(app: Application):
    app.add_handler(ChatJoinRequestHandler(chat_join, CHAT_ID))
    app.add_handler(MessageHandler(Chat(CHAT_ID), delete_system_message))


async def chat_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    questions = [
        """Привет и добро пожаловать в наш клуб!

        Расскажи, что привело тебя к нам и откуда о нас узнал?
        """
    ]
    context.bot.send_message(
        chat_id=CHAT_ID,
        message_thread_id=MAIN_TOPIC_ID,
        text=dedent(choice(questions)),
    )
    await update.message.delete()


async def delete_system_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.message_thread_id is None:
        await update.message.delete()
