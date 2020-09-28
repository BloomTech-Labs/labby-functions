# Core imports

# Third party imports
from airtable import Airtable

BASE_ID = "appvMqcwCQosrsHhM"

TABLE_NAME = "Labs - TBAssignments"


def assign_student_to_project(student: dict, project: dict, score: int, run_id: str):
    """
    Assigns a student to a project in the Team Builder Runs (TBRuns) table
    """
    projects_table = Airtable(BASE_ID, TABLE_NAME)

    project_id = project["id"]

    student_id = student["fields"]["What is your name?"][0]

    print(f"Adding student ({student_id}) to project ({project_id})")

    projects_table.insert(
        {"Run ID": run_id, "Project Link": [project_id], "Student Link": [student_id], "Assignment Score": score}
    )
