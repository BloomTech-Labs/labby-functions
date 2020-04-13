# Core imports

# Third party imports
from airtable import Airtable

SMT_BASE_ID = 'appvMqcwCQosrsHhM'

PROJECTS_TABLE = 'Labs - TBProjects'
PROJECTS_WHERE_COHORT_AND_ACTIVE = '''AND(UPPER({{Cohort}}) = UPPER("{}"), {{Active?}} = True())'''


def get_all_active_projects(cohort: str) -> list:
    """
    Retrieves records for all active projects in a cohort

    Returns:
        records (``list``): List of people records
    """
    projects_table = Airtable(SMT_BASE_ID, PROJECTS_TABLE)

    return projects_table.get_all(formula=PROJECTS_WHERE_COHORT_AND_ACTIVE.format(cohort))


def assign_student_to_project(student: dict, project: dict, score: int):
    """
    Assigns a student to a project
    """
    projects_table = Airtable(SMT_BASE_ID, PROJECTS_TABLE)

    project_id = project['id']
    project_name = project['fields']['Name - Cohort']
    current_project_record = projects_table.get(project_id)

    # print(student)
    student_id = student['fields']['What is your name?'][0]
    student_name = student['fields']['What is your name?'][0]

    team_members = []
    if 'Team Members' in current_project_record['fields']:
        team_members = current_project_record['fields']['Team Members']

        if student_id not in team_members:
            print("Adding {} to team {}".format(student_name, project_name))
            team_members.append(student_id)
    else:
        print("Creating new team assigning {} to team {}".format(student_name, project_name))
        team_members = [student_id]

    print("Updating Airtable project record: {}".format(project_id))
    projects_table.update(project['id'], {'Team Members': team_members})


# @lru_cache(maxsize=32)
# def get_smt_record(record_id: str) -> object:
#     """
#     Retrieves a record from the SMT

#     Returns:
#         record (``object``): An SMT record
#     """
#     airtable = Airtable(SMT_BASE_ID, SMT_STUDENTS_TABLE)

#     return airtable.get(record_id)


# @lru_cache(maxsize=32)
# def get_person_memory(person_smt_record_id: str) -> object:
#     dynamodb_resource: ServiceResource = boto3.resource('dynamodb')
#     person_memory_table: Table = dynamodb_resource.Table(DYNAMODB_PERSON_MEMORY_TABLE)

#     person_item = object
#     try:
#         person_item = person_memory_table.get_item(Key={'person_smt_record_id': person_smt_record_id})
#     except ClientError as e:
#         print("Error getting person memory item: {}".format(
#             e.response['Error']['Message']))

#     return person_item


# def notified_of_interview(person_smt_record_id: str):
#     dynamodb_resource: ServiceResource = boto3.resource('dynamodb')
#     person_memory_table = dynamodb_resource.Table(DYNAMODB_PERSON_MEMORY_TABLE)

#     try:
#         person_memory_table.update_item(Key={'person_smt_record_id': person_smt_record_id},
#                                         UpdateExpression="SET last_interview_notification = :l",
#                                         ExpressionAttributeValues={
#             ':l': datetime.utcnow().isoformat()
#         })
#     except ClientError as e:
#         print("Error updating person memory item: {}".format(
#             e.response['Error']['Message']))


# # @lru_cache(maxsize=32)
# # def get_student_record_by_github_id(github_id: str) -> object:
# #     """
# #     Retrieves a student record from the Labs Base using their github id

# #     Returns:
# #         record (``object``): A student record
# #     """
# #     airtable = Airtable(LABBY_BASE_ID, LABBY_PEOPLE_TABLE)

# #     formula = GET_STUDENT_BY_GITHUB_HANDLE.format(github_id)
# #     print("Executing formula: {}".format(formula))

# #     return airtable.get_all(formula=formula)


# # @lru_cache(maxsize=32)
# # def get_active_student_record_by_smt_record_id(smt_record_id: str) -> object:
# #     """
# #     Retrieves a student record from the Labs Base using their github id

# #     Returns:
# #         record (``object``): A student record
# #     """
# #     airtable = Airtable(LABS_BASE_ID, LABS_STUDENTS_TABLE)

# #     formula = GET_ACTIVE_STUDENT_BY_SMT_RECORD_ID.format(smt_record_id)
# #     print("Executing formula: {}".format(formula))

# #     return airtable.get_all(formula=formula)


# # def insert_student_push(labs_student_record_id: str, github_id: str, timestamp: datetime, repository_id: str):
# #     """
# #     Records a student's Git push event
# #     """
# #     airtable = Airtable(LABS_BASE_ID, LABS_STUDENT_GITHUB_ACTIVITY_TABLE)

# #     record = {"Student Record Link": [labs_student_record_id],
# #               "Timestamp": timestamp.isoformat(),
# #               "Github Repository ID": str(repository_id),
# #               "Event Type": "Push"}

# #     print("Inserting Github activity record: {}".format(record))
# #     return airtable.insert(record)
