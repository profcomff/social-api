"""Работа с чатом Viribus Unitis https://t.me/ViribusUnitisGroup

Для создания нового обработчика создай асинхронную функцию в конце файла с параметрами
Update и Context, а потом зарегистрируй ее внутри функции `register_handlers`.
"""
import logging
from string import ascii_letters, digits, punctuation
from textwrap import dedent
from random import choice

from telegram import Update
from telegram.error import TelegramError
from telegram.ext import (
    Application,
    MessageHandler,
    CommandHandler,
)
from telegram.ext.filters import (
    Chat
)

from social.settings import get_settings
from social.telegram.utils import CustomContext


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
    app.add_handler(CommandHandler(filters=Chat(CHAT_ID), callback=change_slug, command="slug"))
    app.add_handler(MessageHandler(filters=Chat(CHAT_ID), callback=delete_system_message))
    logger.info("Viribus Unitis handlers activated")


async def delete_system_message(update: Update, context: CustomContext):
    """Удаляет сообщения в сервисном канале и отправляет приветственные сообщения"""
    for user in update.effective_message.new_chat_members:
        await context.bot.send_message(
            chat_id=CHAT_ID,
            message_thread_id=MAIN_TOPIC_ID,
            text=dedent(choice(GREETINGS)).format(
                name=user.name, id=user.id
            ),
            parse_mode='markdown',
        )
        logger.info(f"User {user.name} greeting sent")

    if update.effective_message.message_thread_id is None and not update.effective_user.is_bot:
        res = await update.effective_message.delete()
        logger.info(f"Non-bot message to general channel handled, delete status = {res}")


async def change_slug(update: Update, context: CustomContext):
    """Если пользователь является администратором, то он может поменять надпись у имени"""
    logger.info(f'Trying to change slug via command {update.effective_message.text}')
    slug = ' '.join(context.args) if context.args else ''
    if len(slug) == 0:
        await context.bot.send_message(
            chat_id=update.effective_message.chat.id,
            reply_to_message_id=update.effective_message.id,
            text=dedent("""
                Эта команда меняет текст, который пишется справа от имени пользователя в этом чате
                Текст толжен содержать только буквы, цифры, пробелы и некоторую пунктуацию, не более 16 символов
                Напиши `/slug текст` для применения
            """),
            parse_mode='markdown',
        )
        return
    if len(slug) > 16:
        await context.bot.send_message(
            chat_id=update.effective_message.chat.id,
            reply_to_message_id=update.effective_message.id,
            text="Статус должен быть не больше 16 символов",
        )
        return
    if len(set(slug.lower()) - set(digits + ascii_letters + punctuation + 'абвгдеёжзиклмнопрстуфхцчшщъыьэюя ')) != 0:
        await context.bot.send_message(
            chat_id=update.effective_message.chat.id,
            reply_to_message_id=update.effective_message.id,
            text="Текст толжен содержать только буквы, цифры, пробелы и некоторую пунктуацию, не более 16 символов",
        )
        return
    if update.effective_user.id not in [a.user.id for a in await update.effective_chat.get_administrators()]:
        await context.bot.send_message(
            chat_id=update.effective_message.chat.id,
            reply_to_message_id=update.effective_message.id,
            text="Только администраторы могут иметь поясняющий текст",
        )
        return

    try:
        res = await context.bot.set_chat_administrator_custom_title(CHAT_ID, update.effective_user.id, slug)
    except TelegramError as e:
        logger.error(e, exc_info=True)
        res = False
    if not res:
        logger.info('Can not change value', exc_info=True)
        await context.bot.send_message(
            chat_id=update.effective_message.chat.id,
            reply_to_message_id=update.effective_message.id,
            text="Что-то пошло не так и поменять текст не получилось :(",
        )
