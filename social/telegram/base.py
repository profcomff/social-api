from dataclasses import dataclass
import logging
from functools import lru_cache

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CallbackContext,
    CommandHandler,
    ContextTypes,
    ExtBot,
    TypeHandler,
)

from social.settings import get_settings


logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class WebhookUpdate:
    """Simple dataclass to wrap a custom update type"""

    user_id: int
    payload: str


class CustomContext(CallbackContext[ExtBot, dict, dict, dict]):
    """
    Custom CallbackContext class that makes `user_data` available for updates of type
    `WebhookUpdate`.
    """

    @classmethod
    def from_update(
        cls,
        update: object,
        application: "Application",
    ) -> "CustomContext":
        if isinstance(update, WebhookUpdate):
            return cls(application=application, user_id=update.user_id)
        return super().from_update(update, application)


@lru_cache()
def get_application():
    context_types = ContextTypes(context=CustomContext)
    app = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).updater(None).context_types(context_types).build()
    return app
