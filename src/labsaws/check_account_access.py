# Standard imports
import os

# 3rd pary imports
import boto3
import botocore

CORE_STACK_NAME = "labs-student-account-base"

CORE_TEMPLATE = "student_account_core.yaml"


def handler(event, context):
    """Lambda handler for checking whether Labby has access to all student product accounts

    Arguments:
    event   -- Ignored
    context -- Ignored
    """

    # First, we need to assume the Labby role in the root account
    root_accoount_id = os.environ["ROOT_ACCOUNT_ID"]
    root_account_role_arn = f"arn:aws:iam::{root_accoount_id}:role/labby"
    sts_client = boto3.client("sts")

    try:
        assumed_role_in_root_account = sts_client.assume_role(RoleArn=root_account_role_arn, RoleSessionName="Labby")
    except botocore.exceptions.ClientError as ex:
        # TODO - Need to send this error to a log or Slack channel somewhere
        error_message = ex.response["Error"]["Message"]
        print(f"{error_message}")
        print(f"Failed to assument root account role: {root_account_role_arn}")
        raise

    print(f"Successfully assumed the root account role: {root_account_role_arn}")

    # We need the resource ID of the Student OU in the AWS Organization
    root_account_credentials = assumed_role_in_root_account["Credentials"]
    org_client = boto3.client(
        "organizations",
        aws_access_key_id=root_account_credentials["AccessKeyId"],
        aws_secret_access_key=root_account_credentials["SecretAccessKey"],
        aws_session_token=root_account_credentials["SessionToken"],
    )

    # Get a list of all the accounts in the student OU
    student_account_ou_id = os.environ["STUDENT_ACCOUNT_OU_ID"]
    list_accounts_for_parent_paginator = org_client.get_paginator("list_accounts_for_parent")
    student_accounts = list_accounts_for_parent_paginator.paginate(ParentId=student_account_ou_id)

    # Iterate through all of the accounts
    for student_accounts_page in student_accounts:
        for student_account in student_accounts_page["Accounts"]:
            # Assume the admin role in the Student Product Account - This should be auto-created in each account
            student_account_role_arn = f"arn:aws:iam::{student_account['Id']}:role/labby"

            # Assume the Labby role in each child account
            sts_client = boto3.client("sts")

            try:
                assumed_role_in_student_account = sts_client.assume_role(
                    RoleArn=student_account_role_arn, RoleSessionName="labby"
                )
            except botocore.exceptions.ClientError as ex:
                # TODO - Need to send this error to a log or Slack channel somewhere
                error_message = ex.response["Error"]["Message"]
                print(f"{error_message}")
                print(
                    f"Unable to assume student account role ({student_account_role_arn}) from root account role ({root_account_role_arn})"
                )
                continue

            print(
                f"Successfully assumed student account role ({student_account_role_arn}) from root account role ({root_account_role_arn})"
            )

            # List the account aliases using the assumed role
            student_account_credentials = assumed_role_in_student_account["Credentials"]
            iam_client = boto3.client(
                "iam",
                aws_access_key_id=student_account_credentials["AccessKeyId"],
                aws_secret_access_key=student_account_credentials["SecretAccessKey"],
                aws_session_token=student_account_credentials["SessionToken"],
            )

            # List account aliases through the pagination interface
            account_alises_paginator = iam_client.get_paginator("list_account_aliases")
            for page in account_alises_paginator.paginate():
                print(f"Aliases: {page['AccountAliases']}")
