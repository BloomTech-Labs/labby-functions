"""Manages the Lambda Labs integration with Code Climate.

This module contains AWS Lambda function handlers.
"""
# Standard library imports
import random
import os
import multiprocessing

# Third party imports
import boto3

# Local imports
from labscodeclimate import dao as codeclimate_dao
from labsgithub import dao as github_dao
from labsdao import repos as labs_dao


def enqueue_all_product_repos(event, context):
    """Gets a list of all current product repositories and queues them up in
       SQS for processing.

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
    print("Sending {} repositories to the processing queue"
          .format(org_repos.totalCount))

    # Send messages to the worker queues
    code_climate_worker_sqs_queue = os.environ["CODECLIMATE_REPO_WORKER_SQS_URL"]
    github_repo_config_worker_sqs_queue = os.environ["GITHUB_REPO_CONFIG_WORKER_SQS_URL"]

    # TODO: Should be pushing to an SNS topic that is subscribed to by multiple queues
    # TODO: Should json.dumps() to create the message in valid JSON
    for repo in org_repos:
        print("Queueing up repository {} into worker queue: {}"
              .format(repo.full_name, str(code_climate_worker_sqs_queue)))

        response = sqs.send_message(
            QueueUrl=code_climate_worker_sqs_queue,
            # Add some random delay to the messages to throttle the API calls a bit
            DelaySeconds=random.randint(5, 600),
            MessageBody=str(repo.full_name)
        )

        print("Response from SQS: {}".format(response))

        print("Queueing up repository {} into worker queue: {}"
              .format(repo.full_name, str(github_repo_config_worker_sqs_queue)))

        response = sqs.send_message(
            QueueUrl=github_repo_config_worker_sqs_queue,
            # Add some random delay to the messages to throttle the API calls a bit
            DelaySeconds=random.randint(5, 600),
            MessageBody=str(repo.raw_data)
        )

        print("Response from SQS: {}".format(response))

    print("Successfully enqueued {} events".format(org_repos.totalCount))

    return None


def process_repository_batch(event, context):
    event_records = event['Records']
    print("Processing {} events".format(len(event_records)))
    processes = []

    for record in event_records:
        p = multiprocessing.Process(target=__process_repository, args=(record,))
        processes.append(p)
        p.start()

    for process in processes:
        process.join()


def __process_repository(record):
    print("Processing event record: {}".format(record))
    repository_id: str = record['body']

    print("Ensuring repo {} in connected to Code Climate"
          .format(repository_id))
    codeclimate_repo = codeclimate_dao.get_repo(repository_id)

    if codeclimate_repo is None:
        print("Unable to get repo {} from Code Climate, will try later"
              .format(repository_id))
        return None

    print("Getting most recent GPA for repo {}".format(codeclimate_repo))
    gpa = __get_most_recent_gpa(codeclimate_repo)

    print("Getting badge_token for repo {}".format(repository_id))
    badge_token = __get_badge_token(codeclimate_repo)

    print("Getting reporter_id for repo {}".format(repository_id))
    test_reporter_id = __get_test_reporter_id(codeclimate_repo)

    labs_dao.upsert_repository_record(repository_id=repository_id,
                                      grade=gpa,
                                      badge_token=badge_token,
                                      test_reporter_id=test_reporter_id)

    print("Processed event record: {}".format(record))

    return None


def __get_badge_token(codeclimate_repo: dict) -> str:
    if 'attributes' not in codeclimate_repo:
        print("Unable to retrieve badge token for {} 'attributes' field missing".format(codeclimate_repo))
        return "N/A"

    if 'badge_token' not in codeclimate_repo['attributes']:
        print("Unable to retrieve badge token for {} 'badge_token' field missing from 'attributes'".format(codeclimate_repo))
        return "N/A"

    return codeclimate_repo['attributes']['badge_token']


def __get_test_reporter_id(codeclimate_repo: dict) -> str:
    if 'attributes' not in codeclimate_repo:
        print("Unable to retrieve test reporter id for {} 'attributes' field missing".format(codeclimate_repo))
        return "N/A"

    if 'test_reporter_id' not in codeclimate_repo['attributes']:
        print("Unable to retrieve test reporter id for {} 'test_reporter_id' field missing from 'attributes'".format(codeclimate_repo))
        return "N/A"

    return codeclimate_repo['attributes']['test_reporter_id']


def __get_most_recent_gpa(codeclimate_repo: dict) -> str:
    """Returns the most recent GPA (letter grade) for a Github repository.

       Side effect: If the repository is not already integrated with Code Climate, it will be integrated and None will be returned.

    Arguments:
        github_slug {str} -- The Github slug (<owner>/<repository>)

    Returns:
        str -- A letter grade or None if the grade isn't available
    """

    if 'relationships' not in codeclimate_repo:
        print("Unable to retrieve GPA, 'relationships' field missing from {}".format(codeclimate_repo))
        return "N/A"

    relationships = codeclimate_repo['relationships']

    print("{}".format(relationships))
    print("{}".format(relationships['latest_default_branch_snapshot']))
    print("{}".format(relationships['latest_default_branch_snapshot']['data']))

    if ('latest_default_branch_snapshot' not in relationships
            or 'data' not in relationships['latest_default_branch_snapshot']
            or not relationships['latest_default_branch_snapshot']['data']
            or 'id' not in relationships['latest_default_branch_snapshot']['data']):
        return "N/A"

    repo_id = codeclimate_repo['id']
    latest_snapshot_id = relationships['latest_default_branch_snapshot']['data']['id']

    snapshot_json = codeclimate_dao.get_snapshot(repo_id, latest_snapshot_id)

    print("Latest snapshot for repo {}: {}".format("TODO", snapshot_json))

    if ('data' not in snapshot_json
            or 'attributes' not in snapshot_json['data']
            or 'ratings' not in snapshot_json['data']['attributes']):
        return "N/A"

    ratings = snapshot_json['data']['attributes']['ratings']

    print("Ratings for repo {}: {}".format("TODO", ratings))

    if len(ratings) == 0:
        return "N/A"

    latest_rating = ratings[0]

    return latest_rating['letter']
