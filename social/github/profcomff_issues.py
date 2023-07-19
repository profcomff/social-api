import logging
from datetime import datetime, timedelta

from .base import event
from social.utils.github_api import github


logger = logging.getLogger(__name__)


PROJECT_NODE_ID = "PVT_kwDOBaPiZM4AFiz-"
DEADLINE_FIELD_NODE_ID = "PVTF_lADOBaPiZM4AFiz-zgHTmbk"
TAKEN_FIELD_NODE_ID = "PVTF_lADOBaPiZM4AFiz-zgHTme8"


@event(issue=..., action="opened")
def issue_assigned(event):
    logger.debug("Issue %s created (node_id=%s)", event["issue"].get("url"), event["issue"].get("node_id"))
    r = github.request_gql(
        'social/github/profcomff_issues.gql',
        'AddToScrum',
        projectId=PROJECT_NODE_ID,
        contentId=event["issue"].get("node_id")
    )
    logging.debug("Response %s", r)
