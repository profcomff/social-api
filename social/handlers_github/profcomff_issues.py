import datetime
import logging

from social.handlers_github.base import event
from social.utils.github_api import get_github


logger = logging.getLogger(__name__)
github = get_github('profcomff')


PROJECT_NODE_ID = "PVT_kwDOBaPiZM4AFiz-"  # Доска Твой ФФ
DEADLINE_FIELD_NODE_ID = "PVTF_lADOBaPiZM4AFiz-zgHTmbk"  # Поле Deadline для задач на доске Твой ФФ
TAKEN_FIELD_NODE_ID = "PVTF_lADOBaPiZM4AFiz-zgHTme8"  # Поле Taken для задач на доске Твой ФФ


@event(issue=..., action="opened")
def issue_opened(event):
    """При открытии новой issue добавляет ее на доску "Твой ФФ" """
    logger.debug("Issue %s created (node_id=%s)", event["issue"].get("url"), event["issue"].get("node_id"))
    r = github.request_gql(
        'social/handlers_github/profcomff_issues.graphql',
        'AddToScrum',
        projectId=PROJECT_NODE_ID,
        contentId=event["issue"].get("node_id"),
    )
    logging.debug("Response %s", r)


@event(issue=..., action="assigned")
def issue_opened(event):
    """
    При назначении исполнителя для issue,
    если дедлайн не назначен, то назначить дедлайн +неделю от текущей даты
    если дедлайн просрочен (то есть смена исполнителя), то назначает дедлайн +неделю от текущей даты

    так же при назначении исполнителя установить taken_date на текущий день
    впоследствии не менять, даже при смене исполнителя
    """

    # Получение project_item_id, деделайна и даты взятия в работу для текущей issue
    logger.debug("Issue %s assigned (node_id=%s)", event["issue"].get("url"), event["issue"].get("node_id"))
    r = github.request_gql(
        'social/handlers_github/profcomff_issues.graphql',
        'GetIssueDeadlineField',
        issueId=event["issue"].get("node_id"),
    )
    logging.debug("Get Project Fields: %s", r)

    # Парсинг полей
    project_item_id = r['node']['projectItems']['nodes'][0]['id']
    deadline_date = None
    taken_date = None
    for node in r['node']['projectItems']['nodes'][0]['fieldValues']['nodes']:
        if len(node) != 0 and node['field']['name'] == 'Deadline':
            deadline_date = datetime.datetime.strptime(node['date'], '%Y-%m-%d').date()
        if len(node) != 0 and node['field']['name'] == 'Taken':
            taken_date = datetime.datetime.strptime(node['date'], '%Y-%m-%d').date()

    # Изменение дедлайна если требуется
    if deadline_date is None or deadline_date < datetime.date.today():
        new_deadline_date = str((datetime.date.today() + datetime.timedelta(days=7)))
        logging.debug(f"Try to change DeadlineDate from {deadline_date} to {new_deadline_date}")
        r = github.request_gql(
            'social/handlers_github/profcomff_issues.graphql',
            'SetFieldDateValue',
            projectId=PROJECT_NODE_ID,
            itemId=project_item_id,
            fieldId=DEADLINE_FIELD_NODE_ID,
            newDate=new_deadline_date,
        )
        logging.debug("Deadline change response: %s", r)

    # Изменение даты взятия в работу если не назначена
    if taken_date is None:
        new_taken_date = str(datetime.date.today())
        logging.debug(f"Try to change TakenDate from {taken_date} to {new_taken_date}")
        r = github.request_gql(
            'social/handlers_github/profcomff_issues.graphql',
            'SetFieldDateValue',
            projectId=PROJECT_NODE_ID,
            itemId=project_item_id,
            fieldId=TAKEN_FIELD_NODE_ID,
            newDate=new_taken_date,
        )
        logging.debug("Taken change response: %s", r)
