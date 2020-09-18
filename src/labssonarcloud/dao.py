# Standard library imports
import os

# Third party imports
import requests
from typing import Optional

def get_project() -> dict:
    """get a project from sonarcloud

    Returns:
        dict s
    """