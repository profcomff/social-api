import logging
from functools import lru_cache
from textwrap import dedent

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from social.settings import get_settings
from social.utils.telegram_groups import approve_telegram_group

from .handlers_viribus import register_handlers
from .utils import CustomContext


logger = logging.getLogger(__name__)
settings = get_settings()


@lru_cache()
def get_application():
    if not settings.TELEGRAM_BOT_TOKEN:
        return None
    context_types = ContextTypes(context=CustomContext)
    app = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).updater(None).context_types(context_types).build()
    logger.info("Telegram API initialized successfully")
    # Общие хэндлеры
    app.add_handler(CommandHandler(callback=send_help, command="help"))
    app.add_handler(CommandHandler(callback=get_validate, command="validate"))

    # Хэндлеры конкретных чатов
    register_handlers(app)

    return app


async def send_help(update: Update, context: CustomContext):
    await context.bot.send_message(
        chat_id=update.effective_message.chat.id,
        reply_to_message_id=update.effective_message.id,
        text=dedent(
            """
            Привет, я ответственный за печеньки!
            Моя основная цель – помогать различным комьюнити расти
        """
        ),
        parse_mode='markdown',
    )


async def get_validate(update: Update, context: CustomContext):
    approve_telegram_group(update)
    res = await update.effective_message.delete()
    logger.info(f"Validation message handled, delete status = {res}")
