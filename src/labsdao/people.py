# Core imports
from datetime import datetime
from functools import lru_cache

# Third party imports
import boto3
from botocore.exceptions import ClientError
from airtable import Airtable

SMT_BASE_ID = "appvMqcwCQosrsHhM"
# SMT_STUDENTS_TABLE = 'Students'

LABS_STUDENTS_TABLE = "Labs - Students"

STUDENTS_SURVEYS_TABLE = "Labs - TBSurveys"
# STUDENT_SURVEYS_WHERE_COHORT = '''AND(UPPER({{Cohort}}) = UPPER("{}"), UPPER({{What track are you in?}}) != "UX", UPPER({{What track are you in?}}) != "WEB")'''
STUDENT_SURVEYS_WHERE_COHORT = '''UPPER({{Student Course}}) != "UX"'''

LABS_STUDENT_GITHUB_ACTIVITY_TABLE = "Student Github Activity"

LABBY_BASE_ID = "appJ2MpPg4tBiJhOC"
LABBY_PEOPLE_TABLE = "People"

DYNAMODB_PERSON_MEMORY_TABLE = "LabbyPersonMemory"

UNASSIGNED_AND_INCOMPLETE_INTERVIEWEE_FILTER = """AND({Identified for Interview} != '',
                                                      {Cohort Active?} = True(),
                                                      {Interview Scheduled} = False(),
                                                      {Mock Interview Score} = 0,
                                                      {Assigned Interviewer} != '')"""

GET_STUDENT_BY_GITHUB_HANDLE = """LOWER({{Github ID}}) = LOWER("{}")"""

GET_ACTIVE_STUDENT_BY_SMT_RECORD_ID = (
    """AND({{SMT Record ID}} = "{}", {{Cohort Active?}} = True())"""
)


def get_all_student_surveys(cohort: str) -> list:
    """
    Retrieves records for all students onboarding surveys in a cohort

    Returns:
        records (``list``): List of people records
    """
    students_table = Airtable(SMT_BASE_ID, STUDENTS_SURVEYS_TABLE)

    return students_table.get_all(
        view="Labs PT10",
        formula=STUDENT_SURVEYS_WHERE_COHORT.format(cohort),
        sort=[
            "Student Course",
            (
                "If you have a preference, please choose up to 3 types of product you would like to contribute to:",
                "desc",
            ),
        ],
    )


# @lru_cache(maxsize=32)
# def get_all_unscheduled_and_incomplete_interviewees() -> list:
#     """
#     Retrieves records for all interviewees that need an interview, but haven't been scheduled

#     Returns:
#         records (``list``): List of people records
#     """
#     students_table = Airtable(SMT_BASE_ID, LABBY_STUDENTS_TABLE)

#     return students_table.get_all(formula=UNASSIGNED_AND_INCOMPLETE_INTERVIEWEE_FILTER)


# @lru_cache(maxsize=32)
# def get_smt_record(record_id: str) -> object:
#     """
#     Retrieves a record from the SMT

#     Returns:
#         record (``object``): An SMT record
#     """
#     airtable = Airtable(SMT_BASE_ID, SMT_STUDENTS_TABLE)

#     return airtable.get(record_id)


@lru_cache(maxsize=32)
def get_person_memory(person_smt_record_id: str) -> object:
    dynamodb_resource: ServiceResource = boto3.resource("dynamodb")
    person_memory_table: Table = dynamodb_resource.Table(DYNAMODB_PERSON_MEMORY_TABLE)

    person_item = object
    try:
        person_item = person_memory_table.get_item(
            Key={"person_smt_record_id": person_smt_record_id}
        )
    except ClientError as e:
        print(
            "Error getting person memory item: {}".format(
                e.response["Error"]["Message"]
            )
        )

    return person_item


def notified_of_interview(person_smt_record_id: str):
    dynamodb_resource: ServiceResource = boto3.resource("dynamodb")
    person_memory_table = dynamodb_resource.Table(DYNAMODB_PERSON_MEMORY_TABLE)

    try:
        person_memory_table.update_item(
            Key={"person_smt_record_id": person_smt_record_id},
            UpdateExpression="SET last_interview_notification = :l",
            ExpressionAttributeValues={":l": datetime.utcnow().isoformat()},
        )
    except ClientError as e:
        print(
            "Error updating person memory item: {}".format(
                e.response["Error"]["Message"]
            )
        )


@lru_cache(maxsize=32)
def get_student_record_by_github_id(github_id: str) -> object:
    """
    Retrieves a student record from the Labs Base using their github id

    Returns:
        record (``object``): A student record
    """
    airtable = Airtable(LABBY_BASE_ID, LABBY_PEOPLE_TABLE)

    formula = GET_STUDENT_BY_GITHUB_HANDLE.format(github_id)
    print("Executing formula: {}".format(formula))

    return airtable.get_all(formula=formula)


@lru_cache(maxsize=32)
def get_active_student_record_by_smt_record_id(smt_record_id: str) -> object:
    """
    Retrieves a student record from the Labs Base using their github id

    Returns:
        record (``object``): A student record
    """
    airtable = Airtable(LABS_BASE_ID, LABS_STUDENTS_TABLE)

    formula = GET_ACTIVE_STUDENT_BY_SMT_RECORD_ID.format(smt_record_id)
    print("Executing formula: {}".format(formula))

    return airtable.get_all(formula=formula)


def insert_student_push(
    labs_student_record_id: str, github_id: str, timestamp: datetime, repository_id: str
):
    """
    Records a student's Git push event
    """
    airtable = Airtable(LABS_BASE_ID, LABS_STUDENT_GITHUB_ACTIVITY_TABLE)

    record = {
        "Student Record Link": [labs_student_record_id],
        "Timestamp": timestamp.isoformat(),
        "Github Repository ID": str(repository_id),
        "Event Type": "Push",
    }

    print("Inserting Github activity record: {}".format(record))
    return airtable.insert(record)
