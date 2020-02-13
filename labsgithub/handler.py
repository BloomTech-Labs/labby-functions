"""Functions that manage GitHub repository configuration

This module contains AWS Lambda function handlers.
"""
# Standard library imports
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
    event_records: List[dict] = event['Records']
    print("Processing {} events".format(len(event_records)))
    processes = []

    for record in event_records:
        p = multiprocessing.Process(target=__process_repository, args=(record,))
        processes.append(p)
        p.start()

    for process in processes:
        process.join()


def __process_repository(event_record):
    print("Processing event record: {}".format(event_record))
    repo_record_string = event_record['body']
    print("repo_record_string: {}".format(repo_record_string))

    repo_record = ast.literal_eval(repo_record_string)
    print("repo_record: {}".format(repo_record))

    github_api: Github = github_dao.get_api()

    repo: Repository = github_api.get_repo(repo_record['full_name'])

    if __is_labs_repo(repo):
        print("Found Labs repo {}".format(repo.full_name))

        __confirm_student_teams(repo)

        __confirm_collaborators(repo)

        __confirm_master_branch_protection(repo)

        __confirm_repo_configuration(repo)

    return None


def __is_current_team_name(team_name: str) -> bool:
    valid_team_names: List[str] = ['Labs 20', 'Labs PT7']
    up_team_name: str = team_name.upper()
    result = any(up_team_name.find(name.upper()) > -1 for name in valid_team_names)
    if result:
        return True
    return False


def __is_labs_repo(repo: Repository):
    teams: PaginatedList = repo.get_teams()

    team: Team
    for team in teams:
        team_name: str = team.name
        if __is_current_team_name(team_name):
            return True

    return False


def __confirm_student_teams(repo: Repository):
    teams: PaginatedList = repo.get_teams()
    # update current teams only, considering buildons
    team: Team
    for team in teams:
        team_name: str = team.name
        if __is_current_team_name(team_name):
            team.set_repo_permission(repo, "push")


def __confirm_collaborators(repo: Repository):
    collaborators: PaginatedList = repo.get_collaborators()

    collaborator: NamedUser
    for collaborator in collaborators:
        membership: Membership = collaborator.get_organization_membership(repo.organization)
        print("Collaborator {} on repo {} has org membership of {}".format(collaborator.login, repo.full_name, membership))
        if membership is not None and membership.role == "admin":
            print("Removing collaborator {} from repo {} as they are already an org admin".format(collaborator.login, repo.full_name))
            repo.remove_from_collaborators(collaborator)
        else:
            current_permission = repo.get_collaborator_permission(collaborator)
            if current_permission.upper() != "push".upper():
                print("Collaborator {} permission on repo {} being changed from {} to 'push'".format(collaborator.login, repo.full_name, current_permission))

                repo.add_to_collaborators(collaborator, "push")


def __confirm_master_branch_protection(repo: Repository):
    try:
        master_branch: Branch = repo.get_branch("master")
    except GithubException:
        print("Master branch not found for repo {}".format(repo.full_name))
        return

    print("Confirming branch protection for {} branch of repo {}".format(master_branch.name, repo.full_name))
    master_branch.edit_protection(required_approving_review_count=1, enforce_admins=False)
    print("Confirmed branch protection for {} branch of repo {}".format(master_branch.name, repo.full_name))


def __confirm_repo_configuration(repo: Repository):
    if repo.delete_branch_on_merge is not True:
        repo.edit(delete_branch_on_merge=True)
