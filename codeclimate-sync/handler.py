import json
import jwt
import os
from datetime import datetime
from datetime import timedelta
from github import Github
from github import GithubIntegration
import requests
import boto3


def enqueueAllAccounts(event, context):
    githubAPIKey = os.environ["GITHUB_API_KEY"]
    
    githubIntegration = GithubIntegration(integration_id=42806, private_key=githubAPIKey)
    accessToken = githubIntegration.get_access_token(installation_id=2476474)

    print(accessToken.token)
    
    githubAPI = Github(login_or_token=accessToken.token)

    githubOrganization = githubAPI.get_organization("Lambda-School-Labs")

    repos = githubOrganization.get_repos(sort="full_name")

    sqs = boto3.client('sqs')
    dirtyReposQueue = os.environ["DIRTY_REPOS_SQS_URL"]

    print("Dirty Repos Queue: " + str(dirtyReposQueue))

    # repoNames = []
    for repo in repos:
        response = sqs.send_message(
            QueueUrl=dirtyReposQueue,
            DelaySeconds=10,
            MessageBody=str(repo.html_url)
        )

        print(response['MessageId'])

    body = {
        "message": "Installed Repos:" + str(repos),
        "input": event
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response

def reconsileAccounts(event, context):
    githubAPIKey = os.environ["GITHUB_API_KEY"]
    githubAPIClientID = os.environ["GITHUB_API_APP_ID"]
    codeClimateAPIKey = os.environ["CODE_CLIMATE_API_KEY"]

    print(githubAPIKey)
    print(githubAPIClientID)

    githubIntegration = GithubIntegration(integration_id=42806, private_key=githubAPIKey)
    accessToken = githubIntegration.get_access_token(installation_id=2476474)

    print(accessToken.token)
    
    githubAPI = Github(login_or_token=accessToken.token)

    githubOrganization = githubAPI.get_organization("Lambda-School-Labs")

    repos = githubOrganization.get_repos(sort="full_name")

    print(repos)

    headers = {"Accept": "application/vnd.api+json",
                   "Content-Type": "application/vnd.api+json",
                   "Authorization": "Token token=" + codeClimateAPIKey}

    # repoNames = []
    for repo in repos:
        print(repo.html_url)
        

        data  = {
                    "data": {
                        "type": "repos",
                        "attributes": {
                            "url": repo.html_url
                        }
                    }
                }

        print(data)
        response = requests.post(headers=headers,
                                 url="https://api.codeclimate.com/v1/github/repos",
                                 json=data)
        print(response)
        print(response.reason)
        print(response.content)

        # repoNames.append(repo.name)

    body = {
        "message": "Installed Repos:" + str(repos),
        "input": event
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response
