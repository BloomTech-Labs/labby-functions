# Core imports

# Third party imports
from cachetools import cached, TTLCache
from airtable import Airtable
from gql import gql

# Local imports
from ..atlas import auth

SMT_BASE_ID = "appvMqcwCQosrsHhM"

STUDENTS_SURVEYS_TABLE = "Labs - TBSurveys"


def get_all_student_surveys(cohort: str) -> list:
    """
    Retrieves records for all students onboarding surveys in a cohort

    Note: Surveys are gathered from a view on the survey table with the same
          name as the `cohort` parameter.

    Returns:
        records (``list``): List of student survey records
    """
    students_table = Airtable(SMT_BASE_ID, STUDENTS_SURVEYS_TABLE)

    return students_table.get_all(view=cohort)


@cached(cache=TTLCache(maxsize=1024, ttl=600))
def get_student_by_email(email: str) -> dict:
    # Get a client for calling Atlas
    client = auth.client()

    # Provide a GraphQL query
    query = gql(
        """
            query Query($searchTerm: String!) {
                studentsBySearchTerm(term: $searchTerm) {
                    students {
                        id
                        currentSection {
                            id
                            name
                        }
                        user {
                            email
                        }
                    }
                }
            }
        """
    )

    params = {"searchTerm": email}

    # Execute the query on the transport
    print(f"Executing search for student by email {email}")
    result = client.execute(query, variable_values=params)

    print(f"Query result: {result}")

    students = result["studentsBySearchTerm"]["students"]

    # No students with that email were found
    if len(students) == 0:
        return None

    # Multiple students with that email were found
    if len(students) > 1:
        raise (f"Found {len(students)} students for email {email}")

    # Found just one student for that email
    return students[0]
