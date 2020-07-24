from flask import Flask, render_template, request
from github import Github

from longhorn_github_bot.config import get_config

app = Flask(__name__)

config = get_config()
GITHUB_OWNER = config('github_owner')
GITHUB_REPOSITORY = config('github_repository')
ZENHUB_PIPELINE = config('zenhub_pipeline')

g = Github(config('github_token'))


@app.route('/zenhub', methods=['POST'])
def zenhub():
    form = request.form
    organization = form.get('organization')
    repo = form.get('repo')
    if organization != GITHUB_OWNER or repo != GITHUB_REPOSITORY:
        app.logger.debug("webhook event targets %s/%s, ignoring", organization, repo)
    else:
        webhook_type = request.form.get('type')
        if webhook_type == 'issue_transfer':
            issue_transfer(form)
        else:
            app.logger.debug('unhandled webhook type %s, ignoring', webhook_type)

    return {
        'message': 'webhook handled successfully'
    }, 200


def issue_transfer(form):
    issue_number = form.get('issue_number')
    try:
        issue_number = int(issue_number)
    except ValueError:
        app.logger.warning('could not parse issue_number %s as int', issue_number)
        return
    pipeline = form.get('to_pipeline_name')
    if pipeline != ZENHUB_PIPELINE:
        app.logger.debug('to_pipeline is {}, ignoring'.format(pipeline))
        return

    repo = g.get_repo('{}/{}'.format(GITHUB_OWNER, GITHUB_REPOSITORY))
    issue = repo.get_issue(issue_number)
    comments = issue.get_comments()
    found = False
    for comment in comments:
        if comment.body.startswith('## Pre-merged Checklist'):
            app.logger.debug('pre-merged checklist already exists, not creating a new one')
            found = True
            break
    if not found:
        app.logger.debug('pre-merge checklist does not exist, creating a new one')
        issue.create_comment(render_template('pre-merge.md'))
