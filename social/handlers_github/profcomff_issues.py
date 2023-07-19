import json
import logging

# from social.utils.github_api import get_github

from social.handlers_github.base import event


logger = logging.getLogger(__name__)
# github = get_github('profcomff')

from social.handlers_github.delete_me import Github
github = Github()

PROJECT_NODE_ID = "PVT_kwDOBaPiZM4AFiz-"  # Доска Твой ФФ
DEADLINE_FIELD_NODE_ID = "PVTF_lADOBaPiZM4AFiz-zgHTmbk"  # Поле Deadline для задач на доске Твой ФФ
TAKEN_FIELD_NODE_ID = "PVTF_lADOBaPiZM4AFiz-zgHTme8"  # Поле Taken для задач на доске Твой ФФ


# @event(issue=..., action="opened")
# def issue_opened(event):
#     """При открытии новой issue добавляет ее на доску "Твой ФФ" """
#     logger.debug("Issue %s created (node_id=%s)", event["issue"].get("url"), event["issue"].get("node_id"))
#     r = github.request_gql(
#         'social/handlers_github/profcomff_issues.graphql',
#         'AddToScrum',
#         projectId=PROJECT_NODE_ID,
#         contentId=event["issue"].get("node_id"),
#     )
#     logging.debug("Response %s", r)


# @event(issue=..., action="assigned")
def issue_opened(event):
    """
    При назначении исполнителя для issue,
    если дедлайн не назначен, то назначает дедлайн +неделю от текущей даты
    если дедлайн просрочен (то есть смена исполнителя), то назначает дедлайн +неделю от текущей даты
    """
    logger.debug("Issue %s assigned (node_id=%s)", event["issue"].get("url"), event["issue"].get("node_id"))
    r = github.request_gql(
        'social/handlers_github/profcomff_issues.graphql',
        'GetIssueDeadlineField',
        issueId="I_kwDOJKPa4c5sDObA",  # TODO: event["issue"].get("node_id")
    )

    projectItemId = r['node']['projectItems']['nodes'][0]['id']
    deadlineDate = None
    takenDate = None
    for node in r['node']['projectItems']['nodes'][0]['fieldValues']['nodes']:
        if len(node) != 0 and node['field']['name'] == 'Deadline':
            deadlineDate = node['date']
        if len(node) != 0 and node['field']['name'] == 'Taken':
            takenDate = node['date']

    print(projectItemId, deadlineDate, takenDate)
    # r = github.request_gql(
    #     'social/handlers_github/profcomff_issues.graphql',
    #     'SetFieldDateValue',
    #     issueId="I_kwDOJKPa4c5sDObA",
    # )
    logging.debug("Response %s", r)


if __name__ == "__main__":
    with open('test_event.txt') as f:
        event = json.load(f)
    issue_opened(event)