# Third party imports
import boto3

def aws_deprovision_users(event, context):
    return __get_all_org_users()

def __get_all_org_users():
    all_users = []
    client = boto3.client('organizations')
    # TODO: access students org only
    response = client.list_accounts()
    for account in response['Accounts']:
        all_users.append(account['Email'])
    return all_users