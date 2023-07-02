import re
from dataclasses import dataclass
from telegram.ext import (
    Application,
    CallbackContext,
    ExtBot,
)


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


def clear_command(msg):
    return re.sub(r"/\w+(@\w+)?", "", msg, 1, re.IGNORECASE | re.DOTALL).strip()
