# Third party imports
from airtable import Airtable

SMT_BASE_ID = 'appvMqcwCQosrsHhM'

LABS_BASE_ID = 'appThDY89pV0kOGQT'
LABS_CODE_CLIMATE_METRICS_TABLE = 'Code Climate Metrics'

LABBY_BASE_ID = 'appJ2MpPg4tBiJhOC'


def get_all_active() -> list:
    """
    Retrieves all records repetitively and returns a single list.

    Returns:
        records (``list``): An SMT record
    """
    airtable = Airtable(LABBY_BASE_ID, 'Product Github Repos')

    return airtable.get_all(formula="Active = TRUE()")


def update(record_id, record_fields) -> None:
    """[summary]

    Arguments:
        record_id {[type]} -- [description]
        record_fields {[type]} -- [description]
    """
    airtable = Airtable(LABBY_BASE_ID, 'Product Github Repos')

    airtable.update(record_id, record_fields)


def get_all_active_students() -> list:
    """
    Retrieves all active student records

    Returns:
        records (``list``): List of student records
    """
    airtable = Airtable(LABS_BASE_ID, 'Students')

    return airtable.get_all(fields='Name', formula="{Cohort Active?} = TRUE()")


def get_students_by_sprint_retros_submission(days) -> list:
    """
    Retrieves a list of student sprint retro records submitted within the past # of _days_

    Returns:
        records (``list``): List of student sprint retro records
    """
    airtable = Airtable(LABS_BASE_ID, 'Students')

    formula = "AND({{Cohort Active?}} = TRUE(), {{Name}} != '', {{Days Since Last Student Sprint Retro}} > {})".format(days)
    return airtable.get_all(fields=['Name', 'Days Since Last Student Sprint Retro', 'SMT Record ID'], formula=formula, max_records=20)


def get_all_product_github_repo_records():
    """[summary]

    Returns:
        [type] -- [description]
    """
    airtable = Airtable(LABBY_BASE_ID, 'Product Github Repos')

    return airtable.get_all()


def upsert_repository_record(repository_id: str, grade: str, badge_token: str, test_reporter_id: str):
    """
    Updates the grade record for a repository
    """
    airtable = Airtable(LABS_BASE_ID, LABS_CODE_CLIMATE_METRICS_TABLE)

    # Formulate the record to be upserted
    record = {
        "Repository ID": repository_id,
        "Grade": grade,
        "Badge Token": badge_token,
        "Test Reporter ID": test_reporter_id,
    }

    # Search for the record
    formula = "{{Repository ID}} = '{}'".format(repository_id)
    records = airtable.get_all(formula=formula)

    if len(records) == 0:
        # No record, insert a new one
        airtable.insert(record)
        return
    elif len(records) == 1:
        # Record exists, update it
        airtable.update(records[0]['id'], record)
        return

    # Multiple records found, panic!
    raise Exception("Multiple records found for repository ID: {}".format(repository_id))
