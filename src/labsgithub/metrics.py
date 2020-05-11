# Standard library imports
import json
import os
from datetime import datetime

# Local imports
from labsdao import people
from labsgithub import dao as github_dao


def push_hook(event: dict):
    """Receives a web hook from Github for each repository push and forwards to metrics log.

    Arguments:
        event {dict} -- Web hook event from API Gateway
    """
    # Sanity check on the incoming event
    if(not event['headers']['X-GitHub-Event']):
        return {
            'statusCode': 400
        }

    event_type = event['headers']['X-GitHub-Event']
    print("Processing Github event: {}".format(event_type))

    if(event_type == 'push'):
        body = json.loads(event['body'])

        print("Processing event: {}".format(event))
        print("Processing event body: {}".format(body))
        print("Processing event headers: {}".format(event['headers']))
        print("Processing event path: {}".format(event['path']))
        print("Processing event queryStringParameters: {}".format(
            event['queryStringParameters']))

        github_id = body['pusher']['name'].lower()
        repository = body['repository']['name'].lower()
        repository_id = body['repository']['id']

        pushed_at_seconds = body['repository']['pushed_at']
        pushed_at = datetime.utcfromtimestamp(pushed_at_seconds)

        print("User {} pushed to repository {} ({}) at {}".format(
            github_id, repository, repository_id, pushed_at))

        labby_student_record = people.get_student_record_by_github_id(github_id)
        print("Student Record for Github ID {}: {}".format(
            github_id, labby_student_record))

        print("Student record found using Github ID {}: {}".format(
            github_id, labby_student_record))
        smt_record_id = labby_student_record['fields']['SMT Record ID']

        labs_student_record = people.get_active_student_record_by_smt_record_id(
            smt_record_id=smt_record_id)
        print("Active Labs Student Record: {}".format(labs_student_record))

        if not labs_student_record or len(labs_student_record) == 0:
            print("Labs record not found using SMT Record ID {}".format(
                smt_record_id))
        elif len(labs_student_record) > 1:
            print("Multiple student records found using SMT Record ID {}".format(
                smt_record_id))
        else:
            labs_student_record_id = labs_student_record[0]['id']

            people.insert_student_push(labs_student_record_id=labs_student_record_id,
                                       github_id=github_id,
                                       timestamp=pushed_at,
                                       repository_id=repository_id)

    return {
        'statusCode': 200
    }


def reconcile_push_events():
    """Processes all push events in an organization and updates metrics.

       This is used in combination with the web hook to ensure correct metrics even if an event or events are lost.
    """
    github_api = github_dao.get_api()

    github_org_name = os.environ["GITHUB_ORG"]
    github_organization = github_api.get_organization(github_org_name)

    github_events = github_organization.get_events()

    for event in github_events:
        if event.type == "PushEvent":
            print("Processing event {}: {}".format(event.id, event.payload))
            github_id = event.actor.login

            student_record = __get_student_record_by_github_id(github_id)
            print("Got student record for github id {}: {}". format(
                github_id, student_record))

            labs_student_record_id = student_record['id']
            pushed_at = event.created_at
            repository_id = event.repo.id

            print("Processing event {} - {} - {} - {}".format(pushed_at,
                                                              github_id, repository_id, labs_student_record_id))

            # Work in progress
            # people.insert_student_push(labs_student_record_id=labs_student_record_id,
            #                            github_id=github_id,
            #                            timestamp=pushed_at,
            #                            repository_id=repository_id)


def __get_student_record_by_github_id(github_id) -> dict:

    student_record = people.get_student_record_by_github_id(github_id)

    print("Student Record for Github ID {}: {}".format(github_id, student_record))

    if not student_record or len(student_record) == 0:
        print("Student record not found using Github ID {}".format(github_id))
        return None
    elif len(student_record) > 1:
        print("Multiple student records found using Github ID {}".format(github_id))
        raise Exception(
            "Multiple student records found using Github ID {}".format(github_id))
    else:
        print("Student record found using Github ID {}: {}".format(
            github_id, student_record))
        return student_record[0]
