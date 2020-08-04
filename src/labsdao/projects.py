# Core imports

# Third party imports
from airtable import Airtable

SMT_BASE_ID = "appvMqcwCQosrsHhM"

PROJECTS_TABLE = "Labs - Projects"

PROJECTS_WHERE_COHORT_AND_ACTIVE = (
    """AND(UPPER({{Cohort}}) = UPPER("{}"), {{Active?}} = True())"""
)


def get_all_active_projects(cohort: str) -> list:
    """
    Retrieves records for all active projects in a cohort

    Returns:
        records (``list``): List of people records
    """
    projects_table = Airtable(SMT_BASE_ID, PROJECTS_TABLE)

    return projects_table.get_all(
        formula=PROJECTS_WHERE_COHORT_AND_ACTIVE.format(cohort)
    )


def assign_student_to_project(student: dict, project: dict, score: int):
    """
    Assigns a student to a project
    """
    projects_table = Airtable(SMT_BASE_ID, PROJECTS_TABLE)

    project_id = project["id"]
    project_name = project["fields"]["Name"]
    current_project_record = projects_table.get(project_id)

    student_id = student["fields"]["What is your name?"][0]
    student_name = student["fields"]["What is your name?"][0]

    team_members = []
    if "Team Members" in current_project_record["fields"]:
        team_members = current_project_record["fields"]["Team Members"]

        if student_id not in team_members:
            print(f"Adding {student_name} to team {project_name}")
            team_members.append(student_id)
    else:
        print(
            "Creating new team assigning {} to team {}".format(
                student_name, project_name
            )
        )
        team_members = [student_id]

    print("Updating Airtable project record: {}".format(project_id))
    projects_table.update(project["id"], {"Team Members": team_members})
