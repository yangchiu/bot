from jwt import encode
from kubernetes.client import AppsV1Api
from kubernetes.config import load_incluster_config
from requests import post

from datetime import datetime, timedelta
from logging import Logger, StreamHandler
from sys import stdout
from time import sleep

from github_runner_authorizer.config import get_config

COMPONENT_KEY = 'component'
COMPONENT_VALUE = 'github-runner'
ENV_ACCESS_TOKEN = 'ACCESS_TOKEN'
TIME_FORMAT = '%Y-%m-%dT%H:%M:%S%z'

config = get_config()

APP_ID = config('app_id')
INSTALLATION_ID = config('installation_id')
NAMESPACE = config('namespace')
PRIVATE_KEY = config('private_key')

load_incluster_config()
client = AppsV1Api()
logger = Logger(__name__)
logger.addHandler(StreamHandler(stdout))


def patch_template(patch_container):
    return {
        'spec': {
            'template': {
                'spec': {
                    'containers': [
                        patch_container
                    ]
                }
            }
        }
    }


while True:
    iat = datetime.now()
    exp = iat + timedelta(minutes=1)
    token = encode({
        'exp': int(exp.timestamp()),
        'iat': int(iat.timestamp()),
        'iss': APP_ID,
    }, PRIVATE_KEY, 'RS256')

    response = post('https://api.github.com/app/installations/{}/access_tokens'.format(INSTALLATION_ID), headers={
        'Accept': 'application/vnd.github.machine-man-preview+json',
        'Authorization': 'Bearer {}'.format(token.decode('utf-8'))
    }).json()

    replica_sets = client.list_namespaced_replica_set(NAMESPACE)
    for rs in replica_sets.items:
        if rs.metadata.labels.get(COMPONENT_KEY) == COMPONENT_VALUE:
            container = rs.spec.template.spec.containers[0].to_dict()
            for env in container['env']:
                if env.get('name') == ENV_ACCESS_TOKEN:
                    env['value'] = response['token']
                    break
            client.patch_namespaced_replica_set(rs.metadata.name, NAMESPACE, patch_template(container))
            logger.info('Updated ACCESS_TOKEN for {}'.format(rs.metadata.name))

    next_authorization = (datetime.strptime(response['expires_at'], TIME_FORMAT) - datetime.now().astimezone() -
                          timedelta(minutes=10)).seconds
    logger.info('Re-authorizing GitHub runners in {} seconds'.format(next_authorization))
    sleep(next_authorization)
