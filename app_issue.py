from traceback import format_exc
from flask import Blueprint, request
from flask import current_app as app
from github import GitHubAPI
from utils import get_base_dir, get_config, dump_to_json
from app_log import log_request
from crossdomain import crossdomain


app_issue = Blueprint('issue', __name__)
gitHub = GitHubAPI(base_dir=get_base_dir(), **get_config('github'))
api_issue_cors = get_config('api_issue_cors', {'origin', 'headers'})


# stub for receiving events
@app_issue.route('/api/github-gate/', methods=['POST'])
def github_gate():
    log_request(request, 'api-github-gate')
    return 'ok'


def is_issue_request_valid(request):
    exp_keys = {'comment', 'slug', 'before_far', 'before_near', 'sel',
                'after_near', 'after_far'}
    user_data = request.get_json()
    return user_data and user_data.keys() ^ exp_keys == set()


# TODO: escape stars and other md in before*, sel, after*
# TODO: secure as (origin || referer) && (X-Requested-With: XMLHttpRequest)
@app_issue.route('/api/issue/', methods=['POST', 'OPTIONS'])
@crossdomain(**api_issue_cors)
def api_issue():
    log_request(request, 'api-issue')
    # prepare constants
    headers = {'Content-Type': 'application/json; charset=utf-8'}
    bad_payload = {
        'success': False,
        'num': None,
        'url': None,
    }
    bad_request_response = (dump_to_json(bad_payload), 400, headers)
    # get and validate user's data
    if not is_issue_request_valid(request):
        return bad_request_response
    user_data = request.get_json()
    # get template
    exp_keys = {'owner', 'repo', 'title', 'body', 'labels', 'assignees'}
    issue_tmpl = get_config('issue_template', exp_keys)
    # specify template
    as_is_keys = {'owner', 'repo', 'labels', 'assignees'}
    issue = {k: issue_tmpl[k] for k in as_is_keys}
    issue['title'] = issue_tmpl['title'].format_map(user_data)
    issue['body'] = ''
    line_prefix = ''
    for line in issue_tmpl['body']:
        if isinstance(line, dict):
            line_prefix = line['line_prefix']
        else:
            issue['body'] += line_prefix + line.format_map(user_data)
    issue['body'] = issue['body'].rstrip('\n')
    # create issue
    try:
        num, url = gitHub.create_issue(**issue)
        payload = {
            'success': True,
            'num': num,
            'url': url,
        }
    except:
        app.logger.warning(
            'The exception raised in api_issue:\n' + format_exc())
        return bad_request_response
    return (dump_to_json(payload), 200, headers)
