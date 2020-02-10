# Standard library imports
import os
import json

# Third party imports
import requests
from typing import Optional


def __get_headers() -> dict:
    """Helper to get the headers required for an API call

    Returns:
        dict -- Headers for API calls
    """
    headers = {
        "Authorization": "Token token={}".format(os.environ['CODE_CLIMATE_ACCESS_TOKEN'])
    }

    return headers


def get_repo(github_slug: str) -> Optional[dict]:
    url = "https://api.codeclimate.com/v1/repos?github_slug={}".format(github_slug)
    print("Getting repo from Code Climate: {}".format(url))

    response = requests.get(headers=__get_headers(), url=url)
    print("Response from Code Climate to {}: {}-{}".format(url, response, response.text))

    response_json: dict = response.json()
    if len(response_json['data']) == 0:
        print("Repo {} not found, adding to Code Climate".format(github_slug))
        add_repo_to_code_climate(github_slug)
        return None

    return response_json['data'][0]


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
                                                         response.status_code,
                                                         response.text))

    if response.status_code == 201 or response.status_code == 202:
        print("Added {} to Code Climate".format(github_slug))
        return True
    elif response.status_code == 409:
        print("Repo {} was already added to Code Climate".format(github_slug))
        return True

    print("Error adding {} to Code Climate: {}".format(github_slug, response))
    return False
