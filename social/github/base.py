import logging
import re
from typing import Any, Callable


logger = logging.getLogger(__name__)


class EventProcessor:
    """Процессор события

    Имеет фильтры в одном из форматов
    - `поле = маска-регулярное выражение`
    - `поле = lambda-функция`
    - `поле = ...`, просто проверка существования

    Если регулярное выражение удовлетворено, запускает функцию
    """

    def __init__(self, filters: dict[str, str | Callable], function: Callable[[dict[str, Any]], None]):
        self.function = function
        self.filters = {}

        for field, checker in filters.items():
            if isinstance(checker, str):
                logger.debug("Regex filter")
                self.filters[field] = re.compile(checker).match
            elif callable(checker):
                logger.debug("Lambda filter")
                self.filters[field] = checker
            elif checker is ...:
                self.filters[field] = lambda x: True
            else:
                raise TypeError("Filter should be regex or lambda")

    def _check(self, event: dict) -> bool:
        for field, checker in self.filters.items():
            if (value := event.get(field, ...)) is not ... and checker(value):
                logger.debug("field `%s` check ok", field)
                continue
            else:
                logger.debug("field `%s` check fail", field)
                return False
        return True

    def check_and_process(self, event: dict) -> bool | None:
        if self._check(event):
            try:
                logger.debug("Starting fuction")
                self.function(event)
            except Exception as exc:
                logger.error("Can't process event, processor error", exc_info=True)
                return None
            return True
        return False


EVENT_PROCESSORS: list[EventProcessor] = []


def event(**filters: str):
    """Помечает функцию как обработчик событий GitHub, задает фильтры для запуска"""

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
