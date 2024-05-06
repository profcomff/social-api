import logging
from collections.abc import Callable

from social.utils.events import EventProcessor
from social.utils.vk_groups import approve_vk_chat


logger = logging.getLogger(__name__)
EVENT_PROCESSORS: list[EventProcessor] = []


def event(**filters: str):
    """Помечает функцию как обработчик событий, задает фильтры для запуска"""

    def deco(func: Callable):
        EVENT_PROCESSORS.append(EventProcessor(filters, func))
        return func

    return deco


def process_event(event: dict):
    for processor in EVENT_PROCESSORS:
        if processor.check_and_process(event):
            break
    else:
        logger.debug("Event without processor")


@event(
    type="message_new",
    object=lambda i: i.get("message", {}).get("text", "").startswith("/validate"),
)
def validate_group(event: dict):
    """Если получено сообщение команды /validate, то за группой закрепляется владелец"""
    approve_vk_chat(event)
