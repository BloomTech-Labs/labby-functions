"""Manages the Lambda Labs integration with Code Climate.

This module contains AWS Lambda function handlers.
"""
# Standard library imports
import random
import os
import multiprocessing
import logging

# Third party imports
import boto3
import botostubs

# Local imports
from labscodeclimate import dao as codeclimate_dao
from labsgithub import dao as github_dao
from labsdao import repos as labs_dao


def enqueue_all_product_repos(event, context):
    """Gets a list of all current product repositories and queues them up in
       SQS for processing."""
    # Get the queue ready
    sqs_client: botostubs.SQS = boto3.client("sqs")

    print("Connecting to GitHub API")
    github_api = github_dao.get_api()

    GITHUB_ORG_NAME = os.environ["GITHUB_ORG_NAME"]
    print("Connecting to GitHub org: {}".format(GITHUB_ORG_NAME))
    org = github_api.get_organization(GITHUB_ORG_NAME)

    org_repos = org.get_repos()
    print(
        "Sending {} repositories to the processing queue".format(org_repos.totalCount)
    )

    # Send messages to the worker queues
    # TODO: Push to an SNS topic that is subscribed to by multiple queues
    # TODO: Should json.dumps() to create the message in valid JSON
    # TODO: Batch up messages using send_message_batch to speed up processing
    # TODO: Should use multiprocessing to send messages in parallel
    CC_REPO_WORKER_SQS_URL = os.environ["CODECLIMATE_REPO_WORKER_SQS_URL"]
    GH_REPO_CONFIG_WORKER_SQS_URL = os.environ["GITHUB_REPO_CONFIG_WORKER_SQS_URL"]
    for repo in org_repos:
        print(
            "Queueing up repository {} into worker queue: {}".format(
                repo.full_name, str(CC_REPO_WORKER_SQS_URL)
            )
        )

        response = sqs_client.send_message(
            QueueUrl=CC_REPO_WORKER_SQS_URL,
            # Add some random delay to the messages to throttle the API calls
            DelaySeconds=random.randint(5, 900),
            MessageBody={
                "repo.full_name": str(repo.full_name),
                "repo.default_branch": str(repo.default_branch),
            },
        )

        logging.info("Response from SQS: {}".format(response))

        response = sqs_client.send_message(
            QueueUrl=GH_REPO_CONFIG_WORKER_SQS_URL,
            # Add some random delay to the messages to throttle the API calls
            DelaySeconds=random.randint(5, 900),
            MessageBody=str(repo.raw_data),
        )

        print("Response from SQS: {}".format(response))

    print("Successfully enqueued {} events".format(org_repos.totalCount))

    return None


def process_repository_batch(event, context):
    event_records = event["Records"]
    processes = []

    print("Starting {} processes".format(len(event_records)))
    for record in event_records:
        process = multiprocessing.Process(target=__process_repository, args=(record,))
        processes.append(process)
        process.start()

    # Wait for processes to finish before exiting the handler
    logging.info("Waiting for processes to finish")
    for process in processes:
        process.join()


def __process_repository(record):
    print("Processing event record: {}".format(record))
    repo: dict = record["body"]

    print(
        "Ensuring branch {} of repo {} in connected to Code Climate".format(
            repo.default_branch, repo.full_name
        )
    )
    codeclimate_repo = codeclimate_dao.get_repo(repo.full_name)

    if codeclimate_repo is None:
        print("Repo {} not found, adding to Code Climate".format(repo.full_name))
        codeclimate_dao.add_repo_to_code_climate(repo.full_name)
        return None

    print("Getting most recent GPA for repo {}".format(codeclimate_repo))
    gpa = __get_most_recent_gpa(codeclimate_repo)

    print("Getting badge_token for repo {}".format(repo.full_name))
    badge_token = __get_badge_token(codeclimate_repo)

    print("Getting reporter_id for repo {}".format(repo.full_name))
    test_reporter_id = __get_test_reporter_id(codeclimate_repo)

    labs_dao.upsert_repository_record(
        repository_id=repo.full_name,
        grade=gpa,
        badge_token=badge_token,
        test_reporter_id=test_reporter_id,
    )

    print("Processed event record: {}".format(record))

    return None


def __get_badge_token(codeclimate_repo: dict) -> str:
    if "attributes" not in codeclimate_repo:
        print("The 'attributes' field is missing from {}".format(codeclimate_repo))
        return "N/A"

    if "badge_token" not in codeclimate_repo["attributes"]:
        print(
            "The 'attributes.badge_token' field is missing from {}".format(
                codeclimate_repo
            )
        )
        return "N/A"

    return codeclimate_repo["attributes"]["badge_token"]


def __get_test_reporter_id(codeclimate_repo: dict) -> str:
    if "attributes" not in codeclimate_repo:
        print("The 'attributes' field is missing from {}".format(codeclimate_repo))
        return "N/A"

    if "test_reporter_id" not in codeclimate_repo["attributes"]:
        print(
            "The 'attributes.test_reporter_id' field is missung from {}".format(
                codeclimate_repo
            )
        )
        return "N/A"

    return codeclimate_repo["attributes"]["test_reporter_id"]


def __get_most_recent_gpa(codeclimate_repo: dict) -> str:
    """Returns the most recent GPA (letter grade) for a Github repository.

       Side effect: If the repository is not already integrated with
                    Code Climate, it will be integrated and None will
                    be returned.

    Arguments:
        github_slug {str} -- The Github slug (<owner>/<repository>)

    Returns:
        str -- A letter grade or None if the grade isn't available
    """

    if "relationships" not in codeclimate_repo:
        print(
            "Unable to retrieve GPA, 'relationships' field missing from {}".format(
                codeclimate_repo
            )
        )
        return "N/A"

    relationships = codeclimate_repo["relationships"]

    print("{}".format(relationships))
    print("{}".format(relationships["latest_default_branch_snapshot"]))
    print("{}".format(relationships["latest_default_branch_snapshot"]["data"]))

    if (
        "latest_default_branch_snapshot" not in relationships
        or "data" not in relationships["latest_default_branch_snapshot"]
        or not relationships["latest_default_branch_snapshot"]["data"]
        or "id" not in relationships["latest_default_branch_snapshot"]["data"]
    ):
        return "N/A"

    repo_id = codeclimate_repo["id"]
    latest_snapshot_id = relationships["latest_default_branch_snapshot"]["data"]["id"]

    snapshot_json = codeclimate_dao.get_snapshot(repo_id, latest_snapshot_id)

    print("Latest snapshot for repo {}: {}".format("TODO", snapshot_json))

    if (
        "data" not in snapshot_json
        or "attributes" not in snapshot_json["data"]
        or "ratings" not in snapshot_json["data"]["attributes"]
    ):
        return "N/A"

    ratings = snapshot_json["data"]["attributes"]["ratings"]

    print("Ratings for repo {}: {}".format("TODO", ratings))

    if len(ratings) == 0:
        return "N/A"

    latest_rating = ratings[0]

    return latest_rating["letter"]
