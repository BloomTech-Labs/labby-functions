# Standard library imports
import os
import json
from enum import Enum

# Third party imports
import requests


def __get_headers() -> dict:
    """Helper to get the headers required for an API call

    Returns:
        dict -- Headers for API calls
    """
    headers = {
        "Authorization": "Token token={}".format(os.environ['CODE_CLIMATE_API_KEY'])
    }

    return headers


def get_most_recent_gpa(github_slug: str) -> str:
    """Returns the most recent GPA (letter grade) for a Github repository.

       Side effect: If the repository is not already integrated with Code Climate, it will be integrated and None will be returned.

    Arguments:
        github_slug {str} -- The Github slug (<owner>/<repository>)

    Returns:
        str -- A letter grade or None if the grade isn't available
    """
    url = "https://api.codeclimate.com/v1/repos?github_slug={}".format(
        github_slug)
    print("Sending GET requestion to: {}".format(url))

    response = requests.get(headers=__get_headers(), url=url)
    print("Response from GET to {}: {}-{}".format(url, response, response.text))

    response_json = response.json()
    if len(response_json['data']) == 0 or 'relationships' not in response_json['data'][0]:
        add_repo_to_code_climate(github_slug)
        return None

    relationships = response_json['data'][0]['relationships']

    print("{}".format(relationships))
    print("{}".format(relationships['latest_default_branch_snapshot']))
    print("{}".format(relationships['latest_default_branch_snapshot']['data']))

    if ('latest_default_branch_snapshot' not in relationships
            or 'data' not in relationships['latest_default_branch_snapshot']
            or not relationships['latest_default_branch_snapshot']['data']
            or 'id' not in relationships['latest_default_branch_snapshot']['data']
        ):
        return None

    repo_id = response_json['data'][0]['id']
    latest_snapshot_id = relationships['latest_default_branch_snapshot']['data']['id']

    snapshot_json = get_snapshot(repo_id, latest_snapshot_id)

    print("Latest snapshot for repo {}: {}".format(
        github_slug, snapshot_json))

    if ('data' not in snapshot_json
            or 'attributes' not in snapshot_json['data']
            or 'ratings' not in snapshot_json['data']['attributes']
        ):
        return None

    ratings = snapshot_json['data']['attributes']['ratings']

    print("Ratings for repo {}: {}".format(github_slug, ratings))

    if len(ratings) == 0:
        return None

    latest_rating = ratings[0]

    return latest_rating['letter']


def get_snapshot(repository_id: str, snapshot_id: str) -> dict:
    """[summary]

    Arguments:
        repository_id {str} -- [description]
        snapshot_id {str} -- [description]

    Returns:
        dict -- [description]
    """
    url = "https://api.codeclimate.com/v1/repos/{}/snapshots/{}".format(
        repository_id, snapshot_id)

    print("[GET_SNAPSHOT] Sending GET requestion to: {}".format(url))
    response = requests.get(headers=__get_headers(), url=url)
    print("[GET_SNAPSHOT] Response from GET to {}: {}-{}".format(url,
                                                                 response, response.text))

    return response.json()


def add_repo_to_code_climate(github_slug) -> bool:
    url = "https://api.codeclimate.com/v1/github/repos"

    body = {
        "data": {
            "type": "repos",
            "attributes": {
                "url": "https://github.com/{}".format(github_slug)
            }
        }
    }

    print("Posting to URL {}: {}".format(url, json.dumps(body)))
    response = requests.post(headers=__get_headers(), url=url, json=body)

    print("Response from post to URL {}: {} - {}".format(url,
                                                         response.status_code, response.text))

    if response.status_code == 201 or response.status_code == 202:
        print("Added {} to Code Climate".format(github_slug))
        return True

    print("Error adding {} to Code Climate: {}".format(github_slug, response))
    return False
