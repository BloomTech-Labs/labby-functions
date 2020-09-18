"""Manages the Lambda Labs integration with Sonarcloud.

This module contains AWS Lambda function handlers.
"""
# Local imports
from . import dao as sonar_dao
from ..labsgithub import dao as github_dao
# from labsdao import repos as labs_dao

# Standard library imports
import random
import os
import multiprocessing
import logging
logger = logging.getLogger(__name__)
# Third party imports
import boto3
import botostubs

def enqueue_active_product_repos(event, context):
    """Gets a list of all current product repositories and queues them up in
       SQS for processing."""
    # Get the queue ready
    sqs_client: botostubs.SQS = boto3.client("sqs")

    SONAR_ADD_REPO_COMMIT_AGE_MONTHS=1
    SC_REPO_WORKER_SQS_URL = os.environ["SONARCLOUD_REPO_WORKER_SQS_URL"]

    logger.info("Connecting to GitHub API")
    github_api = github_dao.get_api()

    GITHUB_ORG_NAME = os.environ["GITHUB_ORG_NAME"]
    logger.info("Connecting to GitHub org: {}".format(GITHUB_ORG_NAME))
    org = github_api.get_organization(GITHUB_ORG_NAME)

    org_repos = org.get_repos(sort='updated')
    recent_repos = github_dao.filter_commit_age(SONAR_ADD_REPO_COMMIT_AGE_MONTHS, org_repos)
    
    logger.info("{} recent repositories".format(len(recent_repos)))

    for repo in recent_repos:

        response = sqs_client.send_message(
            QueueUrl=SC_REPO_WORKER_SQS_URL,
            # Add some random delay to the messages to throttle the API calls
            DelaySeconds=random.randint(5, 900),
            MessageBody={
                "repo.full_name": str(repo.full_name),
                "repo.default_branch": str(repo.default_branch),
            },
        )
        logging.info("Response from SQS: {}".format(response))

    logger.info("Successfully enqueued {} events".format(len(recent_repos)))

    return recent_repos
