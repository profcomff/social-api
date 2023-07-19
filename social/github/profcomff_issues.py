import logging
from .base import event


logger = logging.getLogger(__name__)


@event(issue=..., action="assigned")
def issue_assigned(event):
    """Если у задачи появился исполнитель – переведи задачу в статус "В работе" и установи время
    начала работы (если не указано), срок выполнения через неделю (если меньше текущего)
    """
    logger.debug("Issue %s assigned", event["issue"].get("url"))
