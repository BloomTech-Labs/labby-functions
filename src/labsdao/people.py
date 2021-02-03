# Core imports
import os
from functools import lru_cache

# Third party imports
from airtable import Airtable

SMT_BASE_ID = "appvMqcwCQosrsHhM"

STUDENTS_SURVEYS_TABLE = "Labs - TBSurveys"
STUDENTS_TABLE = "STUDENTS"

STUDENTS_TABLE_BW_VIEWS = {"FT": "BW Students (FT)", "PTPT": "BW Students (PTPT)", "PTCT": "BW Students (PTCT)"}


def get_all_bw_students(bw_section: str) -> list:
    """
    Retrieves records for all students currently in a particular BW section

    Parameters:
        bw_section (``str``): One of "FT", "PTPT", "PTCT"
    Returns:
        records (``list``): List of student records
    """
    students_table = Airtable(SMT_BASE_ID, STUDENTS_TABLE, api_key=os.environ["AIRTABLE_API_KEY"])

    return students_table.get_all(
        view=STUDENTS_TABLE_BW_VIEWS[bw_section],
        fields=["First Name", "Last Name", "Lambda Email", "Active Track Team"],
    )


def get_all_student_surveys(cohort: str) -> list:
    """
    Retrieves records for all students onboarding surveys in a cohort

    Note: Surveys are gathered from a view on the survey table with the same
          name as the `cohort` parameter.

    Returns:
        records (``list``): List of student survey records
    """
    students_table = Airtable(SMT_BASE_ID, STUDENTS_SURVEYS_TABLE, api_key=os.environ["AIRTABLE_API_KEY"])

    return students_table.get_all(view=cohort)


@lru_cache
def get_student(record_id: str) -> list:
    """
    Retrieves the student record ID

    Returns:
        record: The student record
    """
    students_table = Airtable(SMT_BASE_ID, STUDENTS_SURVEYS_TABLE, api_key=os.environ["AIRTABLE_API_KEY"])

    return students_table.get(record_id)
