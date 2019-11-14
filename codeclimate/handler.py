"""Manages the Lambda Labs integration with Code Climate.

This module contains AWS Lambda function handlers.
"""
# Standard library imports
import json
import jwt
import os
from datetime import datetime
from datetime import timedelta

# Third party imports
import boto3
import requests
from github import Github, UnknownObjectException, GithubIntegration

# Local imports
from dao import metadata    as metadata_dao
from dao import github      as github_dao
from dao import codeclimate as codeclimate_dao
from dao import metadata    as metadata_dao

def enqueue_all_product_repos():
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
    
    github_api = github_dao.get_api()
    
    dirty_repos_queue = os.environ["DIRTY_REPOS_SQS_URL"]
        
    product_github_repo_records = metadata_dao.get_all_product_github_repo_records()
    
    for product_github_repo_record in product_github_repo_records:
        print("Processing record: {}".format(product_github_repo_record))
        
        if "Repo ID" in product_github_repo_record['fields']:
            repository_id = product_github_repo_record['fields']['Repo ID']
            
            try: 
                repo = github_api.get_repo(repository_id)
            except UnknownObjectException as unknown_object_exception:
                print("Could not find repository with ID {}: {}".format(repository_id, unknown_object_exception))
                continue
                
            github_slug = repo.full_name

            print("Queueing up repository with slug {} into SQS queue: {}".format(github_slug, dirty_repos_queue))
            response = sqs.send_message(
                QueueUrl=dirty_repos_queue,
                DelaySeconds=10,
                MessageBody=str(github_slug)
            )

            print("Response from SQS: {}".format(response))


def gather_code_climate_metrics(event):
    """Processes a batch of messages containing Github repository IDs, gathering Code Climate metrics for each repository.
    
    Each repository in the batch is first checked to see if it is already integrated with Code Climate, if not the repository is added to Code Climate using the Code Climate API.
    
    If there are metrics for the repository, they are extracted and stored in the Labs API.
    
    Metrics:
    - Overall repository GPA

    Args:
        event: AWS Lambda handler event

    Returns:
        None

    Raises:
        Nothing
    """
    print("Processing incoming event: {}".format(event))
    
    event_records = event['Records']
    print("Processing {} events".format(len(event_records)))
    
    for record in event_records:
        print("Processing event record: {}".format(record))
        repository_id = record['body']
        
        repository_gpa = codeclimate_dao.get_most_recent_gpa(repository_id)
        
        print("GPA for repository {}: {}".format(repository_id, repository_gpa))
        
        metadata_dao.update_repository_grade(repository_id, repository_gpa)
        
        