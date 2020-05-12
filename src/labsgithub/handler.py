"""Functions that manage GitHub repository configuration

This module contains AWS Lambda function handlers.
"""
# Standard library imports
import logging
import multiprocessing
import ast


# Third party library imports
from typing import List
from github import Github, GithubException, PaginatedList
from github.Membership import Membership
from github.Team import Team
from github.NamedUser import NamedUser
from github.Repository import Repository
from github.Branch import Branch

# Local imports
from labsgithub import dao as github_dao


def repo_configuration_worker(event: dict, context: dict):
    """The handler entry point for processing GitHub repository records.

    Note: This handler uses the multiprocessing library to parallelize processing of records

    event -- Contains a list of event records from the queue
    """
    event_records: List[dict] = event["Records"]
    print("Processing {} events".format(len(event_records)))
    processes = []

    for record in event_records:
        p = multiprocessing.Process(target=__process_repository, args=(record,))
        processes.append(p)
        p.start()

    for process in processes:
        process.join()


def __process_repository(event_record: dict):
    """Processes a single GitHub repository.

    event_record -- An event record from the queue
    """
    print("Processing event record: {}".format(event_record))

    # Extract the 'body' part of the record
    repo_record_string = event_record["body"]
    print("repo_record_string: {}".format(repo_record_string))

    repo_record = ast.literal_eval(repo_record_string)
    print("repo_record: {}".format(repo_record))

    # Get an instance of the GitHub API client
    github_api: Github = github_dao.get_api()

    # Get the repository record from the GitHub API
    repo: Repository = github_api.get_repo(repo_record["full_name"])

    # Check to see if the repo is part of a Labs product
    if __is_labs_repo(repo):
        print("Confirming configuration for Labs repo {}".format(repo.full_name))

        try:
            __confirm_repo_configuration(repo)
        except Exception as err:
            logging.error(
                "Error confirming configuration for Labs repo {}: {}".format(
                    repo.full_name, err
                )
            )


def __confirm_repo_configuration(repo: Repository):
    # __confirm_student_teams(repo)

    # __confirm_collaborators(repo)

    # __confirm_master_branch_protection(repo)

    __confirm_delete_branch_on_merge(repo)

    return None


def __is_labs_team_name(team_name: str) -> bool:
    """Returns true if the team name starts with the string 'Labs' (case insensitive); false otherwise"""
    return team_name.upper().startswith("LABS")


def __is_labs_repo(repo: Repository) -> bool:
    """Returns true if the repository is part of a Labs product; false otherwise

    Currently, a repo is assumed to be part of a Labs product if it has at least one team with
    a name starting with the string 'Labs' (case insensitive)
    """
    teams: PaginatedList = repo.get_teams()

    team: Team
    for team in teams:
        team_name: str = team.name
        if __is_labs_team_name(team_name):
            return True

    return False


def __confirm_student_teams(repo: Repository):
    """Confirms the configuration of student teams on the repo

    Ensures the team has 'push' access to the repository
    """
    teams: PaginatedList = repo.get_teams()
    # update current teams only, considering buildons
    team: Team
    for team in teams:
        team_name: str = team.name

        if __is_labs_team_name(team_name) and "ADMIN" not in team_name.upper():
            team.set_repo_permission(repo, "push")


def __confirm_collaborators(repo: Repository):
    collaborators: PaginatedList = repo.get_collaborators()

    collaborator: NamedUser
    for collaborator in collaborators:
        membership: Membership = collaborator.get_organization_membership(
            repo.organization
        )
        print(
            "Collaborator {} on repo {} has org membership of {}".format(
                collaborator.login, repo.full_name, membership
            )
        )
        if membership is not None and membership.role == "admin":
            print(
                "Removing collaborator {} from repo {} as they are already an org admin".format(
                    collaborator.login, repo.full_name
                )
            )
            repo.remove_from_collaborators(collaborator)
        else:
            current_permission = repo.get_collaborator_permission(collaborator)
            if current_permission.upper() != "push".upper():
                print(
                    "Collaborator {} permission on repo {} being changed from {} to 'push'".format(
                        collaborator.login, repo.full_name, current_permission
                    )
                )

                repo.add_to_collaborators(collaborator, "push")


def __confirm_master_branch_protection(repo: Repository):
    """Confirms master branch protection is configured for the repository.

    The 'master' branch will require 1 approver and admins cannot force a merge.
    """
    try:
        master_branch: Branch = repo.get_branch("master")
    except GithubException:
        print("Master branch not found for repo {}".format(repo.full_name))
        return

    print(
        "Confirming branch protection for {} branch of repo {}".format(
            master_branch.name, repo.full_name
        )
    )
    master_branch.edit_protection(
        required_approving_review_count=1, enforce_admins=False
    )
    print(
        "Confirmed branch protection for {} branch of repo {}".format(
            master_branch.name, repo.full_name
        )
    )


def __confirm_delete_branch_on_merge(repo: Repository):
    if repo.delete_branch_on_merge is not True:
        repo.edit(delete_branch_on_merge=True)
