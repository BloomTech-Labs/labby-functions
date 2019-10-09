import json
import jwt
import os
from datetime import datetime
from datetime import timedelta
from github import Github
from github import GithubIntegration
import requests
import boto3

# Local imports
from dao import metadata
from dao import github

def enqueue_all_accounts(event, context):
    github_api = github.get_api()

    # The Github org to work with
    # TODO: Labby should be able to work with many orgs
    github_org_name = os.environ["GITHUB_ORG"]
    github_organization = github_api.get_organization(github_org_name)

    # Get a list of all the repos in the org
    repos = github_organization.get_repos(sort="full_name")

    # Get the queue ready
    sqs = boto3.client('sqs')
    dirty_repos_queue = os.environ["DIRTY_REPOS_SQS_URL"]

    print("Queueing up {} repos into: {}".format(repos.totalCount, dirty_repos_queue))
    
    for repo in repos:
        print("Queueing up {} into: {}".format(repo.full_name, dirty_repos_queue))
        response = sqs.send_message(
            QueueUrl=dirty_repos_queue,
            DelaySeconds=10,
            MessageBody=str(repo.html_url)
        )

        print(response['MessageId'])

    body = {
        "message": "Queued {} repos".format(repos.totalCount),
        "input": event
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response

def reconsile_accounts(event, context):
    print("Event:\n{}\nContext:\n{}".format(str(event), str(context)))
    
    body = {
        "message": "Event:\n{}\nContext:\n{}".format(str(event), str(context)),
        "input": event
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response
