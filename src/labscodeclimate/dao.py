# Standard library imports
import os

# Third party imports
import requests
from typing import Optional

GET_REPOS_URL = "https://api.codeclimate.com/v1/repos?github_slug={}"
GET_SNAPSHOTS_URL = "https://api.codeclimate.com/v1/repos/{}/snapshots/{}"

POST_REPO = "https://api.codeclimate.com/v1/github/repos"


def __get_required_headers() -> dict:
    """Helper to get the headers required for an API call

    Returns:
        dict -- Headers for API calls
    """
    ACCESS_TOKEN = os.environ["CODE_CLIMATE_ACCESS_TOKEN"]
    headers = {"Authorization": "Token token={}".format(ACCESS_TOKEN)}

    return headers


def get_repo(github_slug: str) -> Optional[dict]:
    """See https://developer.codeclimate.com/#get-repository"""
    url = GET_REPOS_URL.format(github_slug)
    response = requests.get(headers=__get_required_headers(), url=url)

    response_json: dict = response.json()
    if len(response_json["data"]) == 0:
        return None

    return response_json["data"][0]


def get_snapshot(repository_id: str, snapshot_id: str) -> dict:
    """See https://developer.codeclimate.com/#get-snapshot"""
    url = GET_SNAPSHOTS_URL.format(repository_id, snapshot_id)
    response = requests.get(headers=__get_required_headers(), url=url)

    return response.json()


def add_repo_to_code_climate(github_slug) -> bool:
    """https://developer.codeclimate.com/#add-public-oss-repository"""
    body = {
        "data": {
            "type": "repos",
            "attributes": {"url": "https://github.com/{}".format(github_slug)},
        }
    }

    response = requests.post(headers=__get_required_headers(), url=POST_REPO, json=body)

    if response.status_code == 201 or response.status_code == 202:
        print("Added {} to Code Climate".format(github_slug))
        return True
    elif response.status_code == 409:
        print("Repo {} was already added to Code Climate".format(github_slug))
        return True

    print("Error adding {} to Code Climate: {}".format(github_slug, response))
    return False
