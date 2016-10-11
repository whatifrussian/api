import os
from datetime import datetime, timedelta, timezone
import requests
import jwt


class GitHubAPI:
    class InternalError(Exception):
        def __init__(self, desc):
            super(InternalError, self).__init__(desc)

    def __init__(self, secret_key_file, base_dir=None, **kwargs):
        self.API_BASE = 'https://api.github.com'
        self.integration_id = kwargs['integration_id']
        if base_dir:
            self.secret_key_file = os.path.join(base_dir, secret_key_file)
        else:
            self.secret_key_file = secret_key_file
        self.installation_id = kwargs['installation_id']
        self.read_secret_key()

    def read_secret_key(self):
        with open(self.secret_key_file, 'r') as f:
            self.secret_key = f.read()

    def get_jwt(self):
        now = datetime.now(timezone.utc)
        exp = now + timedelta(minutes=1)
        payload = {
            'iat': int(now.timestamp()),
            'exp': int(exp.timestamp()),
            'iss': self.integration_id,
        }
        jwt_bytes = jwt.encode(payload, self.secret_key, algorithm='RS256')
        return jwt_bytes.decode('utf-8')

    def get_token(self):
        url = self.API_BASE + '/installations/{id}/access_tokens'.format(
            id=self.installation_id)
        headers = self.get_headers('jwt')
        response = requests.post(url, headers=headers)
        return response.json()['token']

    def get_headers(self, auth_type):
        headers = {'Accept': 'application/vnd.github.machine-man-preview+json'}
        if auth_type == 'jwt':
            jwt = self.get_jwt()
            headers.update(
                {'Authorization': 'Bearer {jwt}'.format(jwt=jwt)})
        elif auth_type == 'token':
            token = self.get_token()
            headers.update(
                {'Authorization': 'token {token}'.format(token=token)})
        else:
            raise InternalError('auth_type param should be "jwt" or "token"')
        return headers

    def create_issue(self, **kwargs):
        headers = self.get_headers('token')
        payload_fields = ['title', 'body', 'labels', 'assignees']
        payload = {k: kwargs[k] for k in payload_fields}
        url = self.API_BASE + '/repos/{owner}/{repo}/issues'.format(**kwargs)
        response = requests.post(url, json=payload, headers=headers)
        issue_num = response.json()['number']
        issue_url = response.json()['html_url']

        return issue_num, issue_url
