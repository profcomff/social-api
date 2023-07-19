import logging

from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport


class Github:
    def __init__(self, settings):
        self.settings = settings

        self.transport = RequestsHTTPTransport(
            url='https://api.github.com/graphql',
            verify=True,
            retries=1,
            headers={'Authorization': f'Bearer {settings.GH_ACCOUNT_TOKEN}'}
        )

        self.client = Client(transport=self.transport)

        with open('social/utils/scrum.graphql') as f:
            self.q_add_to_scrum = gql(f.read())

    def add_to_scrum(self, issue_id):
        try:
            params = {'projectId': self.settings.GH_SCRUM_ID,
                      'contentId': issue_id}
            r = self.client.execute(self.q_add_to_scrum, operation_name='AddToScrum', variable_values=params)
            item_id = r['addProjectV2ItemById']['item']['id']
            logging.info(f'Node {issue_id} successfully added to scrum with contentId= {issue_id}')
        except Exception as err:
            logging.error(f'Scrum adding FAILED: {err.args}')
