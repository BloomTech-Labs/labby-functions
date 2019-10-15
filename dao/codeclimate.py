# Standard library imports
import os
import requests
from enum import Enum

def is_repo_linked(github_slug) -> bool:
  headers = {
    "Authorization": "Bearer {}".format(os.environ['GITHUB_PERSONAL_ACCESS_TOKEN'])
  }

  url="GET https://api.codeclimate.com/v1/repos?github_slug={}".format(github_slug)
  print(url)
  
  response = requests.post(headers=headers, url=url)
  
  if response.status_code == 200 or response.status_code == 201:
    return True
  else:
    raise False
