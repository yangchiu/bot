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
PROJECT_PIPELINE = config('project_pipeline')
PROJECT_PIPELINE_TRIAGE = "Triage"
PROJECT_PIPELINE_ICEBOX = "Icebox"
PROJECT_PIPELINE_BACKLOG = "Backlog"
PROJECT_NAME = "Longhorn Sprint"

ADD_TO_SPRINT_PIPELINES = {PROJECT_PIPELINE_TRIAGE, PROJECT_PIPELINE_ICEBOX, PROJECT_PIPELINE_BACKLOG}
REMOVE_FROM_SPRINT_PIPELINES = {PROJECT_PIPELINE_TRIAGE, PROJECT_PIPELINE_ICEBOX}

# From https://docs.python.org/3/howto/logging.html#logging-to-a-file
numeric_level = getattr(logging, FLASK_LOGLEVEL.upper(), None)
if not isinstance(numeric_level, int):
    raise ValueError('invalid log level: %s'.format(FLASK_LOGLEVEL))
app.logger.setLevel(level=numeric_level)

g = Github(config('github_token'))

gql_url = "https://api.github.com/graphql"
gql_headers = {"Authorization": f"Bearer {config('github_token')}"}

@auth.verify_password
def verify_password(username, password):
    if check_password_hash(FLASK_USERNAME, username) and check_password_hash(FLASK_PASSWORD, password):
        return username


@app.route('/project', methods=['POST'])
@auth.login_required
def project():
    json = request.get_json()
    print(json)

    organization = json['organization']['login']
    if organization != GITHUB_OWNER:
        app.logger.debug(f"webhook event targets {organization}, ignoring")
        return {
            'message': 'webhook handled successfully'
        }, 200

    if 'action' not in json:
        app.logger.debug(f"unhandled webhook type, ignoring")
        return {
            'message': 'webhook handled successfully'
        }, 200

    webhook_type = json['action']
    if webhook_type != 'edited':
        app.logger.debug(f"unhandled webhook type {webhook_type}, ignoring")
        return {
            'message': 'webhook handled successfully'
        }, 200

    changed_field = json['changes']['field_value']['field_name']
    if changed_field != 'Status':
        app.logger.debug(f"unhandled changed field {changed_field}, ignoring")
        return {
            'message': 'webhook handled successfully'
        }, 200

    issue_transfer(json)
    return {
        'message': 'webhook handled successfully'
    }, 200


def issue_transfer(json):

    issue_node_id = json['projects_v2_item']['content_node_id']

    to_pipeline = json['changes']['field_value']['to']['name']
    from_pipeline = json['changes']['field_value']['to']['name']

    if to_pipeline == PROJECT_PIPELINE:
        add_checklist(issue_node_id)

    if from_pipeline in ADD_TO_SPRINT_PIPELINES and to_pipeline not in ADD_TO_SPRINT_PIPELINES:
        add_to_sprint(issue_number)
    elif from_pipeline not in REMOVE_FROM_SPRINT_PIPELINES and to_pipeline in REMOVE_FROM_SPRINT_PIPELINES:
        remove_from_sprint(issue_number)
    else:
        app.logger.debug('to_pipeline is {}, from_pipeline is {}, ignoring'.format(to_pipeline, from_pipeline))
        return


def add_checklist(issue_node_id):
    repo = g.get_repo(f"{GITHUB_OWNER}/{GITHUB_REPOSITORY}")
    print(f"get issue with number with node id: {issue_node_id}")
    issue_number = query_issue_number(issue_node_id)
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
    active_sprint_id, repository_gh_id = query_active_sprint_id_and_repository_gh_id(PROJECT_NAME)
    issue_id = query_issue_id(repository_gh_id, issue_number)
    add_issue_to_sprint(issue_id, active_sprint_id)


def remove_from_sprint(issue_number):
    active_sprint_id, repository_gh_id = query_active_sprint_id_and_repository_gh_id(PROJECT_NAME)
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

def query_issue_number(issue_node_id):
    query = """
query($issueId: ID!) {
  node(id: $issueId) {
    ... on Issue {
      number
    }
  }
}
            """
    variables = {
        "issueId": issue_node_id
    }
    response = requests.post(url=gql_url,
                             headers=gql_headers,
                             json={
                                 "query": query,
                                 "variables": variables
                             })
    app.logger.debug("query_issue_number response %s %s", response.status_code, response.json())
    issue_number = response.json()["data"]["node"]["number"]
    print(f"issue_number = {issue_number}")
    return issue_number

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
