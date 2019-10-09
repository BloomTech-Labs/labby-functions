# Standard library imports
import json
import os

from enum import Enum

# Local imports
from dao import metadata
from dao import github

# The repository naming convention requires a specific postfix depending on the purpose
class RepositoryPurpose(Enum):
    FRONTEND        = "-fe"
    BACKEND         = "-be"
    DATA_SCIENCE    = "-ds"
    IOS             = "-ios"
    ANDROID         = "-android"
    SITE            = "-site"

def reconsile_all_project_github_repos(event, context):
    github_api = github.get_api()

    # The Github org to work with
    # TODO: Labby should be able to work with many orgs
    github_org_name = os.environ["GITHUB_ORG"]
    github_organization = github_api.get_organization(github_org_name)

    product_github_repos = metadata.get_all_active()

    print("Processing {} repositories".format(len(product_github_repos)))
    for record in product_github_repos:
        if is_record_valid(record):  
            print('============================================================================================================')
            print("Processing record \n{}".format(record))

            # Generate the standardized repository name
            product_name = record['fields']['Product Name'][0]
            repository_purpose = RepositoryPurpose[record['fields']['Purpose'].upper()]
            repository_name = convert_to_repository_name(product_name, repository_purpose)
            
            repo_exists = github.does_repo_exist(github_organization, repository_name)
            if repo_exists:
                # Need to adopt the repo
                print("Adopting: {}".format(repository_name))

                record_updates = {
                    "Repo ID": github_organization.get_repo(repository_name).id,
                    "Repo Name": repository_name
                }
                metadata.update(record['id'], record_updates)
            else:
                # Need to create the repo
                print("Creating: {}".format(repository_name))
                
                repository_id = github.generate_repo(github_org_name, repository_name, record['fields']['Purpose'].upper())
                
                record_updates = {
                        "Repo ID": repository_id,
                        "Repo Name": repository_name
                    }
                    
                metadata.update(record['id'], record_updates)
            print('============================================================================================================\n')


    body = {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "input": event
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response


def is_record_valid(record) -> bool:
    if 'Purpose' not in record['fields']:
        print("Found record missing purpose: {}".format(record['id']))
        return False

    if 'Product Name' not in record['fields']:
        print("Found record with missing product name: {}".format(record['id']))
        return False

    if not isinstance(record['fields']['Product Name'], list):
        print("Found record where Product Name is not a list: {}".format(record['id']))
        return False

    if len(record['fields']['Product Name']) != 1:
        print("Found record where Product Name is not a list with one value: {}".format(record['id']))
        return False

    if 'Repo ID' in record['fields']:
        print("Skipping record with Repo ID: {}".format(record['id']))
        return False

    return True

    
def convert_to_repository_name(product_name: str, repository_purpose: RepositoryPurpose):
    """ 
    Converts repository metadata into a repository name.

    Parameters: 
    productName (string): The name of the repository
    repositoryPurpose (RepositoryPurpose): The purpose of the repository as RepositoryPurpose

    Returns: 
    str: Properly formatted repository name
    """
    if product_name is None:
        raise ValueError('Product name must be provided')

    if repository_purpose is None:
        raise ValueError('Repository purpose must be provided')
    
    # Repository name starts with product name
    repository_name = product_name

    # Remove special characters
    repository_name = repository_name.replace("-", ' ')
    repository_name = repository_name.replace(":", ' ')

    # Remove extra spaces
    repository_name = " ".join(repository_name.split())

    # Convert spaces to dashes
    repository_name = repository_name.replace(" ", '-')

    # Add the postfix
    repository_name = repository_name + repository_purpose.value

    return repository_name.lower()