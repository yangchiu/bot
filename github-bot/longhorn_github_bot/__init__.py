import requests
from flask import Flask, render_template, request
from flask_httpauth import HTTPBasicAuth
from github import Github
from werkzeug.security import generate_password_hash, check_password_hash

from longhorn_github_bot.config import get_config

import logging

app = Flask(__name__)
auth = HTTPBasicAuth()

config = get_config()
FLASK_LOGLEVEL = config('flask_loglevel')
FLASK_PASSWORD = generate_password_hash(config('flask_password'))
FLASK_USERNAME = generate_password_hash(config('flask_username'))
GITHUB_OWNER = config('github_owner')
GITHUB_REPOSITORY = config('github_repository')
ZENHUB_PIPELINE = config('zenhub_pipeline')
ZENHUB_PIPELINE_TRIAGE = "Triage"
ZENHUB_PIPELINE_ICEBOX = "Icebox"
ZENHUB_PIPELINE_BACKLOG = "Backlog"
ZENHUB_WORKSPACE_NAME = "Longhorn Main Board"

ADD_TO_SPRINT_PIPELINES = {ZENHUB_PIPELINE_TRIAGE, ZENHUB_PIPELINE_ICEBOX, ZENHUB_PIPELINE_BACKLOG}
REMOVE_FROM_SPRINT_PIPELINES = {ZENHUB_PIPELINE_TRIAGE, ZENHUB_PIPELINE_ICEBOX}

# From https://docs.python.org/3/howto/logging.html#logging-to-a-file
numeric_level = getattr(logging, FLASK_LOGLEVEL.upper(), None)
if not isinstance(numeric_level, int):
    raise ValueError('invalid log level: %s'.format(FLASK_LOGLEVEL))
app.logger.setLevel(level=numeric_level)

g = Github(config('github_token'))

gql_url = "https://api.zenhub.com/public/graphql"
gql_headers = {"Authorization": f"Bearer {config('zenhub_graphql_token')}"}


@auth.verify_password
def verify_password(username, password):
    if check_password_hash(FLASK_USERNAME, username) and check_password_hash(FLASK_PASSWORD, password):
        return username


@app.route('/zenhub', methods=['POST'])
@auth.login_required
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

    to_pipeline = form.get('to_pipeline_name')
    from_pipeline = form.get('from_pipeline_name')

    if to_pipeline == ZENHUB_PIPELINE:
        add_checklist(issue_number)

    if from_pipeline in ADD_TO_SPRINT_PIPELINES and to_pipeline not in ADD_TO_SPRINT_PIPELINES:
        add_to_sprint(issue_number)
    elif from_pipeline not in REMOVE_FROM_SPRINT_PIPELINES and to_pipeline in REMOVE_FROM_SPRINT_PIPELINES:
        remove_from_sprint(issue_number)
    else:
        app.logger.debug('to_pipeline is {}, from_pipeline is {}, ignoring'.format(to_pipeline, from_pipeline))
        return


def add_checklist(issue_number):
    repo = g.get_repo('{}/{}'.format(GITHUB_OWNER, GITHUB_REPOSITORY))
    issue = repo.get_issue(issue_number)
    comments = issue.get_comments()
    found = False
    for comment in comments:
        if comment.body.strip().startswith('## Pre Ready-For-Testing Checklist'):
            app.logger.debug('pre-merged checklist already exists, not creating a new one')
            found = True
            break
    if not found:
        app.logger.debug('pre-merge checklist does not exist, creating a new one')
        issue.create_comment(render_template('pre-merge.md'))


def add_to_sprint(issue_number):
    active_sprint_id, repository_gh_id = query_active_sprint_id_and_repository_gh_id(ZENHUB_WORKSPACE_NAME)
    issue_id = query_issue_id(repository_gh_id, issue_number)
    add_issue_to_sprint(issue_id, active_sprint_id)


def remove_from_sprint(issue_number):
    active_sprint_id, repository_gh_id = query_active_sprint_id_and_repository_gh_id(ZENHUB_WORKSPACE_NAME)
    issue_id = query_issue_id(repository_gh_id, issue_number)
    remove_issue_from_sprint(issue_id, active_sprint_id)


def query_active_sprint_id_and_repository_gh_id(workspace_name):
    query = """
            query QueryActiveSprintIdAndRepositoryGhId($workspace_name: String!) {
                viewer {
                    searchWorkspaces(query: $workspace_name) {
                        nodes {
                            id
                            name
                            activeSprint {
                                id
                                name
                            }
                            defaultRepository {
                                ghId
                                id
                                name
                            }
                        }
                    }
                }
            }
            """
    variables = {"workspace_name": workspace_name}

    response = requests.post(url=gql_url,
                             headers=gql_headers,
                             json={
                                 "query": query,
                                 "variables": variables
                             })
    app.logger.debug("query_active_sprint_id_and_repository_gh_id response %s %s", response.status_code, response.json())
    active_sprint_id = response.json()["data"]["viewer"]["searchWorkspaces"]["nodes"][0]["activeSprint"]["id"]
    repository_gh_id = response.json()["data"]["viewer"]["searchWorkspaces"]["nodes"][0]["defaultRepository"]["ghId"]
    return active_sprint_id, repository_gh_id


def query_issue_id(repository_gh_id, issue_number):
    query = """
            query QueryIssueId($repository_gh_id: Int!, $issue_number: Int!) {
                issueByInfo(repositoryGhId: $repository_gh_id, issueNumber: $issue_number) {
                    id
                    number
                }
            }
            """
    variables = {
        "repository_gh_id": repository_gh_id,
        "issue_number": issue_number
    }
    response = requests.post(url=gql_url,
                             headers=gql_headers,
                             json={
                                 "query": query,
                                 "variables": variables
                             })
    app.logger.debug("query_issue_id response %s %s", response.status_code, response.json())
    issue_id = response.json()["data"]["issueByInfo"]["id"]
    return issue_id


def add_issue_to_sprint(issue_id, sprint_id):
    query = """
            mutation AddIssueToSprint($issue_id: ID!, $sprint_id: ID!) {
                addIssuesToSprints(input: {
                    issueIds: [$issue_id],
                    sprintIds: [$sprint_id]
                }) {
                    clientMutationId
                }
            }
            """
    variables = {
        "issue_id": issue_id,
        "sprint_id": sprint_id
    }
    response = requests.post(url=gql_url,
                             headers=gql_headers,
                             json={
                                 "query": query,
                                 "variables": variables
                             })
    app.logger.debug("add_issue_to_sprint response %s %s", response.status_code, response.json())
    return response.status_code


def remove_issue_from_sprint(issue_id, sprint_id):
    query = """
            mutation RemoveIssueFromSprint($issue_id: ID!, $sprint_id: ID!) {
                removeIssuesFromSprints(input: {
                    issueIds: [$issue_id],
                    sprintIds: [$sprint_id]
                }) {
                    clientMutationId
                }
            }
            """
    variables = {
        "issue_id": issue_id,
        "sprint_id": sprint_id
    }
    response = requests.post(url=gql_url,
                             headers=gql_headers,
                             json={
                                 "query": query,
                                 "variables": variables
                             })
    app.logger.debug("remove_issue_from_sprint response %s %s", response.status_code, response.json())
    return response.status_code
