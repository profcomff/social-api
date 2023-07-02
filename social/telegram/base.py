import logging
from functools import lru_cache
from textwrap import dedent

from telegram import Update
from telegram.ext import (
    Application,
    ContextTypes,
    CommandHandler,
)

from social.settings import get_settings

from .handlers_viribus import register_handlers
from .utils import CustomContext


logger = logging.getLogger(__name__)
settings = get_settings()


@lru_cache()
def get_application():
    context_types = ContextTypes(context=CustomContext)
    app = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).updater(None).context_types(context_types).build()
    logger.info("Telegram API initialized successfully")
    register_handlers(app)
    app.add_handler(CommandHandler(callback=send_help, command="help"))
    return app


async def send_help(update: Update, context: CustomContext):
    await context.bot.send_message(
        chat_id=update.effective_message.chat.id,
        reply_to_message_id=update.effective_message.id,
        text=dedent("""
            Привет, я ответственный за печеньки!
            Моя основная цель – помогать различным комьюнити расти
        """),
        parse_mode='markdown',
    )
