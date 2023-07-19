import logging
from datetime import datetime, timedelta

from .base import event
from social.utils.github_api import get_github


logger = logging.getLogger(__name__)
github = get_github('profcomff')


PROJECT_NODE_ID = "PVT_kwDOBaPiZM4AFiz-"  # Доска Твой ФФ
DEADLINE_FIELD_NODE_ID = "PVTF_lADOBaPiZM4AFiz-zgHTmbk"  # Поле Deadline для задач на доске Твой ФФ
TAKEN_FIELD_NODE_ID = "PVTF_lADOBaPiZM4AFiz-zgHTme8"     # Поле Taken для задач на доске Твой ФФ


@event(issue=..., action="opened")
def issue_opened(event):
    """При открытиии новой ишью добавляет ее на достку "Твой ФФ"
    """
    logger.debug("Issue %s created (node_id=%s)", event["issue"].get("url"), event["issue"].get("node_id"))
    r = github.request_gql(
        'social/handlers_github/profcomff_issues.gql',
        'AddToScrum',
        projectId=PROJECT_NODE_ID,
        contentId=event["issue"].get("node_id")
    )
    logging.debug("Response %s", r)
