import re
from traceback import format_exc
from flask import Blueprint, request
from flask import current_app as app
from github import GitHubAPI
from utils import get_base_dir, get_config, dump_to_json
from app_log import log_request


app_issue = Blueprint('issue', __name__)
gitHub = GitHubAPI(base_dir=get_base_dir(), **get_config('github'))
escape_md_re = re.compile(r'([*_\\<>\[\]`])')


# stub for receiving events
@app_issue.route('/api/github-gate/', methods=['POST'])
def github_gate():
    log_request(request, 'api-github-gate')
    return 'ok'


def is_issue_request_valid(request):
    exp_headers = {
        'X-Requested-With': ('XMLHttpRequest',),
        'Content-Type': (
            'application/json; charset=utf-8',
            'application/json; charset=UTF-8',
        ),
    }
    for k, exp_v in exp_headers.items():
        value = request.headers.get(k)
        if value not in exp_v:
            exp_v_str = '* "' + '"\n* "'.join(exp_v) + '"'
            why = ('Header "{k}" is "{value}", ' +
                   'expected one of the following:\n' +
                   '{exp_v}').format(k=k, value=value, exp_v=exp_v_str)
            return False, why
    exp_keys = {'comment', 'slug', 'before_far', 'before_near', 'sel',
                'after_near', 'after_far'}
    user_data = request.get_json()
    if not user_data:
        why = 'The request cannot be interpreted as JSON'
        return False, why
    keys = user_data.keys()
    if keys ^ exp_keys != set():
        why = 'Keys are {keys}, expected {exp_keys}'.format(
            keys=keys, exp_keys=exp_keys)
        return False, why
    return True, None


def escape_sel_context(user_data):
    res = dict()
    exp_keys = {'before_far', 'before_near', 'sel', 'after_near', 'after_far'}
    for k, v in user_data.items():
        if k in exp_keys:
            res[k] = escape_md_re.sub(r'\\\1', user_data[k])
        else:
            res[k] = user_data[k]
    return res


@app_issue.route('/api/issue/', methods=['POST'])
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
    valid, why = is_issue_request_valid(request)
    if not valid:
        log_request(request, 'api-issue-errors', why)
        return bad_request_response
    user_data = request.get_json()
    user_data = escape_sel_context(user_data)
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
            line = line.format_map(user_data)
            line = ('\n' + line_prefix).join(line.split('\n'))
            issue['body'] += line_prefix + line
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
        why = 'The exception raised in api_issue:\n' + format_exc()
        app.logger.warning(why)
        log_request(request, 'api-issue-errors', why)
        return bad_request_response
    return (dump_to_json(payload), 200, headers)
