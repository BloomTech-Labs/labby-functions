# Standard library imports
import os
import requests

from enum import Enum

# Third party imports
from github import Github
from github import GithubIntegration
from github import UnknownObjectException

githubRequestHeaders = {
    "Accept": "application/vnd.github.baptiste-preview+json"
}

class RepositoryTemplate(Enum):
    FRONTEND        = "template-fe"
    BACKEND         = "template-be"
    DATA_SCIENCE    = "template-ds"
    IOS             = "template-ios"
    ANDROID         = "template-android"
    SITE            = "template-site"
    
def get_api():
  # This authenticates Labby as a Github App: https://developer.github.com/apps/about-apps/#about-github-apps
  github_app_id = os.environ["GITHUB_API_APP_ID"]
  github_api_key = os.environ["GITHUB_API_KEY"]

  github_integration = GithubIntegration(integration_id=github_app_id, private_key=github_api_key)

  # Grab an access token for the one any only installation
  # TODO: This should handle multiple installations
  github_installation_id = os.environ["GITHUB_INSTALLATION_ID"]
  access_token = github_integration.get_access_token(installation_id=github_installation_id)

  # Use the access token to authenticate for the specific installation
  github_api = Github(login_or_token=access_token.token)

  return github_api

def does_repo_exist(organization, repository_name):
  try:
      organization.get_repo(repository_name)

      return True
  except UnknownObjectException:
      return False

def generate_repo(organization_name, repository_name, repository_purpose) -> int:
  github_request_body = {
    "name": repository_name,
    "owner": organization_name
  }

  githubRequestHeaders["Authorization"] = "Bearer " + os.environ['GITHUB_PERSONAL_ACCESS_TOKEN']
  
  url="https://api.github.com/repos/{}/{}/generate".format(organization_name, RepositoryTemplate[repository_purpose.upper()].value)
  print(url)
  
  response = requests.post(headers=githubRequestHeaders,
                           url=url,
                           json=github_request_body)
  
  if response.status_code == 200 or response.status_code == 201:
    return response.json()['id']
  else:
    raise Exception("Unable to generate repository: {}".format(response.text))
