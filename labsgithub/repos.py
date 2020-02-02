# Standard library imports
import json
import os
from enum import Enum

# Third party imports
import github.GithubException

# Local imports
from labsdao import repos
from labsgithub import dao as github_dao


# The repository naming convention requires a specific postfix depending on the purpose
class RepositoryPurpose(Enum):
    FRONTEND = "-fe"
    BACKEND = "-be"
    DATA_SCIENCE = "-ds"
    MOBILE = "-mobile"
    IOS = "-ios"
    ANDROID = "-android"
    SITE = "-site"


def provision_product_repos():
    """Ensures all product repos are provisioned or adopted.
    """
    print("Connecting to GitHub API")
    github_api = github_dao.get_api()
    
    # The Github org to work with
    # TODO: Labby should be able to work with many orgs
    github_org_name = os.environ["GITHUB_ORG"]
    
    print("Connecting to org: {}".format(github_org_name)
    github_organization = github_api.get_organization(github_org_name)

    product_github_repos = repos.get_all_active()

    print("Processing {} repositories".format(len(product_github_repos)))
    for record in product_github_repos:
        if not __is_product_github_repo_record_valid(record):
            print("Skipping invalid Product Github Repo record\n{}".format(record))
            continue

        repository_name = __generate_repository_name(record)

        if 'Repo ID' not in record['fields']:
            # The repository ID is not known, see if a repository by the same name already exists
            repository = None
            try:
                repository = github_api.get_repo(
                    "{}/{}".format(github_organization.login, repository_name))
            except github.GithubException as e:
                # print("Unable to get repository: {}/{}\n{}".format(github_organization.login, repository_name, e))
                pass

            if not repository:
                # Need to create the repository
                print("Creating repository: {}".format(repository_name))

                repository_purpose = repository_purpose = record['fields']['Purpose']
                repository_id = github_dao.generate_repo(
                    github_org_name, repository_name, repository_purpose)

                record_updates = {
                    "Repo ID": repository_id,
                }
                github_dao.update(record['id'], record_updates)
            else:
                # Need to adopt the repository
                print("Adopting repository: {}".format(repository_name))

                record_updates = {
                    "Repo ID": github_organization.get_repo(repository_name).id,
                }
                github_dao.update(record['id'], record_updates)


def __is_product_github_repo_record_valid(record) -> bool:
    if 'Purpose' not in record['fields']:
        print("Found record missing purpose: {}".format(record['id']))
        return False

    if 'Product Name' not in record['fields']:
        print("Found record with missing product name: {}".format(
            record['id']))
        return False

    if not isinstance(record['fields']['Product Name'], list):
        print("Found record where Product Name is not a list: {}".format(
            record['id']))
        return False

    if len(record['fields']['Product Name']) != 1:
        print("Found record where Product Name is not a list with one value: {}".format(
            record['id']))
        return False

    return True


def __generate_repository_name(record) -> str:
    """ 
    Generates repository name from a Product Github Repo record

    Parameters: 
    record (string): A Product Github Repo record

    Returns: 
    str: Properly formatted repository name
    """
    product_name = record['fields']['Product Name'][0]

    repository_purpose = record['fields']['Purpose']
    repository_purpose_postfix = RepositoryPurpose[repository_purpose.upper(
    )].value

    repository_custom_postfix = ""
    if ('Postfix' in record['fields']):
        repository_custom_postfix = record['fields']['Postfix']

    # Repository name starts with product name
    repository_name = product_name

    # Remove special characters
    repository_name = repository_name.replace("-", ' ')
    repository_name = repository_name.replace(":", ' ')
    repository_name = repository_name.replace("'", '')
    repository_name = repository_name.replace("!", '')

    # Remove extra spaces
    repository_name = " ".join(repository_name.split())

    # Convert spaces to dashes
    repository_name = repository_name.replace(" ", '-')

    # Add the custom postfix
    repository_name = repository_name + repository_custom_postfix

    # Add the purpose postfix
    repository_name = repository_name + repository_purpose_postfix

    return repository_name.lower()
