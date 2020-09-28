# Standard library imports
import os

from enum import Enum

# Third party imports
# Note: https://pygithub.readthedocs.io/en/latest/index.html
#       https://github.com/PyGithub/PyGithub
from github import Github
from github import GithubIntegration
from github import UnknownObjectException

# These are used to authenticate Labby as a Github App
# See https://developer.github.com/apps/about-apps/#about-github-apps
INTEGRATION_ID = os.environ["GITHUB_APP_INTEGRATION_ID"]
PRIVATE_KEY = os.environ["GITHUB_APP_PRIVATE_KEY"]

# This the installation ID for the Labs GitHub org
INSTALLATION_ID = os.environ["GITHUB_APP_ORG_INSTALLATION_ID"]

REQUEST_HEADERS = {"Accept": "application/vnd.github.baptiste-preview+json"}


class RepositoryTemplate(Enum):
    FRONTEND = "template-fe"
    BACKEND = "template-be"
    DATA_SCIENCE = "template-ds"
    IOS = "template-ios"
    ANDROID = "template-android"
    MOBILE = "template-android"
    SITE = "template-site"


def get_api() -> Github:
    """Returns an instance of the API for the Labs org"""
    print(f"Authenticating with integration ID {INTEGRATION_ID} and key {PRIVATE_KEY[0:45]}...")
    integration = GithubIntegration(integration_id=INTEGRATION_ID, private_key=PRIVATE_KEY)

    print("Getting access token for {} from {}".format(INSTALLATION_ID, integration.base_url))

    # Grab an access token for the Labs org installation
    access_token = integration.get_access_token(INSTALLATION_ID)

    # Use the access token to authenticate for the specific installation
    github_api: Github = Github(login_or_token=access_token.token)

    return github_api


def does_repo_exist(organization, repository_name):
    """Returns true if the repo exists in the org, false otherwise"""
    try:
        organization.get_repo(repository_name)

        return True
    except UnknownObjectException:
        return False


# =========================================================
# Temporarily disable
# =========================================================
# def generate_repo(organization_name, repository_name, repository_purpose) -> int:
#     """[summary]

#     Arguments:
#         organization_name {[type]} -- [description]
#         repository_name {[type]} -- [description]
#         repository_purpose {[type]} -- [description]

#     Raises:
#         Exception: [description]

#     Returns:
#         int -- [description]
#     """
#     github_request_body = {
#         "name": repository_name,
#         "owner": organization_name
#     }

#     githubRequestHeaders["Authorization"] = "Bearer " + \
#         os.environ['GITHUB_PERSONAL_ACCESS_TOKEN']

#     url = "https://api.github.com/repos/{}/{}/generate".format(
#         organization_name, RepositoryTemplate[repository_purpose.upper()].value)
#     print(url)

#     response = requests.post(headers=REQUEST_HEADERS,
#                              url=url,
#                              json=github_request_body)

#     if response.status_code == 200 or response.status_code == 201:
#         return response.json()['id']
#     else:
#         raise Exception(
#             "Unable to generate repository: {}".format(response.text))
