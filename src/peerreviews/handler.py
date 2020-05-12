# Standard library imports
import json
import os
import pprint

from enum import Enum

# Third party imports
import slack
from slack.errors import SlackApiError

# Local imports
from labsdao import people

USERNAME = "Labby"
ICON_URL = "https://labby-public-assets.s3.amazonaws.com/labby-small.png"

DAYS_LATE_BEFORE_WARNING = 90


def remind_students_about_late_peer_reviews(event, context):
    """[summary]

    Arguments:
        event {[type]} -- [description]
        context {[type]} -- [description]
    """
    # Grab a list of all currently active students
    students = people.get_students_by_sprint_retros_submission(DAYS_LATE_BEFORE_WARNING)

    # TODO: This is the legacy method for authenticating to the API
    print("Getting slack client")
    slack_api_token = os.environ["SLACK_API_TOKEN"]
    client = slack.WebClient(token=slack_api_token)

    print(
        "Checking {} students with sprint retros older than {} days".format(
            len(students), DAYS_LATE_BEFORE_WARNING
        )
    )
    for student_record in students:
        if not is_student_record_valid(student_record):
            print("Bad Labs Student Record")
            pprint.pprint(student_record)
            continue

        smt_record = people.get_smt_record(student_record["fields"]["SMT Record ID"][0])

        if not is_smt_record_valid(smt_record):
            print("Bad SMT Student Record")
            pprint.pprint(smt_record)
            continue

        first_name = smt_record["fields"]["First Name"][0]
        slack_id = smt_record["fields"]["Slack User ID"][0]

        print(
            "Processing student {} with Slack User ID {}".format(first_name, slack_id)
        )

        message = (
            "Hi {}! I noticed you haven't submitted a Student Sprint Retro form in a while.\n\n"
            "According to the "
            "<https://www.notion.so/lambdaschool/Labs-Forms-and-Attendance-Policy-1e215b21d8ce49a18c56cda298b9471d|Labs Forms and Attendance Policy> "
            "this form needs to be submitted at the end of every week. Please do hurry and submit the form here: "
            "<https://airtable.com/shr8jHfy6r5whBAai|Student Sprint Retro Form>"
            "\n\nIf you've already submitted or don't feel like you need to submit, please talk to your SL right away. Thanks!"
        ).format(first_name)

        # slack_response = client.conversations_open(users=['ULLS6HX6G', 'UKW1FTYER'])
        # print(slack_response)

        # channel_id = slack_response['channel']['id']

        slack_response = client.conversations_open(users=slack_id)
        if slack_response["ok"]:
            channel_id = slack_response["channel"]["id"]
            print("Posting message to {} on channel {}".format(first_name, channel_id))
            try:
                response = client.chat_postMessage(
                    channel=channel_id,
                    text=message,
                    username=USERNAME,
                    icon_url=ICON_URL,
                )
            except SlackApiError as error:
                print("Failed to post message: {}".format(error))
            else:
                if response["ok"] != True:
                    print(
                        "Slack response not ok: {}-{}".format(
                            response.status_code, response["error"]
                        )
                    )

            try:
                response = client.chat_postMessage(
                    channel="#labby_testing",
                    text=message,
                    username=USERNAME,
                    icon_url=ICON_URL,
                )
            except SlackApiError as error:
                print("Failed to post message: {}".format(error))
            else:
                if response["ok"] != True:
                    print(
                        "Slack response not ok: {}-{}".format(
                            response.status_code, response["error"]
                        )
                    )
        else:
            print("Error posting to Slack user {}: {}".format(slack_id, slack_response))


def is_student_record_valid(record) -> bool:
    if "fields" not in record:
        print("Student record has no fields")
        return False

    if "Name" not in record["fields"]:
        print("Student record has no 'Name' field")
        return False

    if "SMT Record ID" not in record["fields"]:
        print("Student record has no 'SMT Record ID' field")
        return False

    if not isinstance(record["fields"]["SMT Record ID"], list):
        print("Expected 'SMT Record ID' field to be a list")
        return False

    if len(record["fields"]["SMT Record ID"]) != 1:
        print("Expected 'SMT Record ID' field to be a list of one")
        return False

    return True


def is_smt_record_valid(record) -> bool:
    if "fields" not in record:
        print("SMT record has no fields")
        return False

    if "First Name" not in record["fields"]:
        print("SMT record has no 'First Name' field")
        return False

    if not isinstance(record["fields"]["First Name"], list):
        print("Expected SMT 'First Name' field to be a list")
        return False

    if not len(record["fields"]["First Name"]) == 1:
        print("Expected SMT 'First Name' field to be a list of one")
        return False

    if "Slack User ID" not in record["fields"]:
        print("SMT record has no 'Slack User ID' field")
        return False

    if not isinstance(record["fields"]["Slack User ID"], list):
        print("Expected SMT 'Slack User ID' field to be a list")
        return False

    if not len(record["fields"]["Slack User ID"]) == 1:
        print("Expected SMT 'Slack User ID' field to be a list of one")
        return False

    return True
