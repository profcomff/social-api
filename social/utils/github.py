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
        params = {'projectId': self.settings.GH_SCRUM_ID, 'contentId': issue_id}
        return self.client.execute(self.q_add_to_scrum, operation_name='AddToScrum', variable_values=params)
