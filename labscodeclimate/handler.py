"""Manages the Lambda Labs integration with Code Climate.

This module contains AWS Lambda function handlers.
"""
# Standard library imports
import random
import json
import os
from datetime import datetime
from datetime import timedelta

# Third party imports
import jwt
import boto3
import requests
from github import Github, UnknownObjectException, GithubIntegration

# Local imports
from labscodeclimate import dao as codeclimate_dao
from labsgithub import dao as github_dao

def enqueue_all_product_repos(event, context):
    """Gets a list of all current product repositories and queues them up in SQS for processing.

    Args:
        None

    Returns:
        None

    Raises:
        Nothing
    """
    # Get the queue ready
    sqs = boto3.client('sqs')

    print("Connecting to GitHub API")
    github_api = github_dao.get_api()
    
    org_name = os.environ["GITHUB_ORG_NAME"]
    print("Connecting to GitHub org: {}".format(org_name))
    org = github_api.get_organization(org_name)
    
    org_repos = org.get_repos()
    print("Sending {} repositories to the processing queue".format(org_repos.totalCount))
    
    # Send messages to the worker queue
    worker_sqs_queue = os.environ["CODECLIMATE_REPO_WORKER_SQS_URL"]
    
    for repo in org_repos:
        print("Queueing up repository {} into worker queue: {}".format(repo.full_name, str(worker_sqs_queue)))
        response = sqs.send_message(
            QueueUrl=worker_sqs_queue,
            # Add some random delay to the messages to throttle the API calls a bit
            DelaySeconds=random.randint(5,300),
            MessageBody=str(repo.full_name)
        )

        print("Response from SQS: {}".format(response))
        

def add_repositories(event, context):
    event_records = event['Records']
    print("Processing {} events".format(len(event_records)))

    for record in event_records:
        print("Processing event record: {}".format(record))
        repository_id = record['body']
        
        print("Processing repo: {}".format(repository_id))
        
        codeclimate_dao.add_repo_to_code_climate(repository_id)
