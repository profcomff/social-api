import logging
import os.path
import time
from datetime import datetime
from functools import lru_cache

import jwt
import requests
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
from graphql import DocumentNode

from social.settings import get_settings


logger = logging.getLogger(__name__)
settings = get_settings()


class GitHub:
    def __init__(self, app_id: int, pem: str, org: str):
        self._app_id = app_id  # App ID
        self._pem: bytes = pem.encode()  # App secret key
        self._org = org  # Name of organization to log into
        self._jwt = None
        self._jwt_expire = None
        self._org_token = None
        self._org_token_expire = None
        self._client = None
        self.client  # Чисто проверка на верные данные

    def _reauth(self) -> tuple[str, time.time]:
        signing_key = jwt.jwk_from_pem(self._pem)

        issued = time.time() - 60
        expiration = time.time() + 600
        logger.debug('JWT issued at %s, expire at %s', issued, expiration)

        payload = {
            # Issued at time
            'iat': int(issued),
            # JWT expiration time (10 minutes maximum)
            'exp': int(expiration),
            # GitHub App's identifier
            'iss': self._app_id,
        }

        # Create JWT
        jwt_instance = jwt.JWT()
        encoded_jwt = jwt_instance.encode(payload, signing_key, alg='RS256')

        self._jwt, self._jwt_expire = encoded_jwt, expiration

    def _update_org_token(self):
        if self._jwt is None or self._jwt_expire is None or self._jwt_expire <= time.time():
            self._reauth()
        r = requests.get(
            f'https://api.github.com/orgs/{self._org}/installation',
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self._jwt}",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )
        logger.debug("Installation request: %s", r)
        installation_token_url = r.json()['access_tokens_url']

        logger.debug("access_tokens_url: %s", installation_token_url)
        r = requests.post(
            installation_token_url,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self._jwt}",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        ).json()
        logger.debug("Token request: %s", r)
        self._org_token = r['token']
        self._org_token_expire = datetime.fromisoformat(r['expires_at']).replace(tzinfo=None)

    @property
    def client(self):
        if (
            self._client is None
            or self._org_token is None
            or self._org_token_expire is None
            or self._org_token_expire <= datetime.utcnow()
        ):
            logger.debug("Updating token")
            self._update_org_token()
            transport = RequestsHTTPTransport(
                url='https://api.github.com/graphql',
                verify=True,
                retries=1,
                headers={'Authorization': f'Bearer {self._org_token}'},
            )
            self._client = Client(transport=transport)
        return self._client

    @lru_cache(30)
    def _read_gql(self, path: str):
        with open(path) as f:
            return gql(f.read())

    def request_gql(self, file_or_query, operation_name, **params):
        logger.debug(os.path.exists(file_or_query))
        if os.path.exists(file_or_query):
            return self.client.execute(self._read_gql(file_or_query), params, operation_name)
        if isinstance(file_or_query, DocumentNode):
            return self.client.execute(file_or_query, params, operation_name)
        else:
            return self.client.execute(gql(file_or_query), params, operation_name)


@lru_cache()
def get_github(org):
    github = GitHub(settings.GITHUB_APP_ID, settings.GITHUB_PRIVATE_KEY, org)
    return github
