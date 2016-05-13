from flask import Flask, render_template, send_file, send_from_directory, redirect, url_for, request

import os
import requests
import json

OAUTH_KEY = os.getenv('OAUTH_KEY', '')
REPO_OWNER = os.getenv('REPO_OWNER', 'whatifrussian')
REPO_NAME = os.getenv('REPO_NAME', 'website')
ISSUE_ASSIGNEE = 'librarian'
ISSUE_LABELS = ['typo']
API_URL='https://api.github.com/repos/{owner}/{repo}/issues'

app = Flask(__name__)
app.debug = True

def create_issue(author, url, text, comment):
    payload = {
        "title": "typo on {url} by {author}".format(url=url, author=author),
        "body": body,
        "assignee": ISSUE_ASSIGNEE,
        "labels": ISSUE_LABELS
    }

    headers = {
        'Content-Type': "application/json; charset=utf-8",
        'Accept': "application/vnd.github.v3+json",
        'Authorization': "token {token}".format(token=OAUTH_KEY),
    }
    response = requests.request("POST", API_URL.format(owner=REPO_OWNER, repo=REPO_NAME), data=json.dumps(payload), headers=headers)

    return response.json().get("html_url", False)

@app.route('/api/issue/', methods=['POST'])
def issue():
    author = request.form['author']
    url = request.form['url']
    text = request.form['text']
    comment = request.form['comment']
    issue_created = create_issue(author, url, text, comment)
    return json.dumps({"result": issue_created}) if issue_created else json.dumps({"result": "error"})

if __name__ == '__main__':
    app.run()