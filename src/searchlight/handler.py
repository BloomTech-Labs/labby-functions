# Standard library imports
import csv
import time

# Local imports
from ..labsdao import projects as projectsdao
from ..labsdao import people as peopledao


def generate_reviewer_csv(event, context):
    """Generates a CSV file with all required reviews for current projects

    Parameters:
        event -- The ID of the cohort (e.g. PT15)
        context -- AWS Lambda context

    Returns:
        Nothing
    """
    if not event:
        raise ("You must provide the cohort ID as data in the event")

    # Use the DAO to grab the list of all active projects
    projects = projectsdao.get_all_active_projects(event)
    print("Found {} projects".format(len(projects)))

    peer_review_assignments = []
    for project in projects:
        team_members = project["fields"]["Team Members"]
        # print("{}".format(team_members))

        for i in range(0, len(team_members)):
            reviewee_id = team_members[i]

            reviewee = peopledao.get_student(reviewee_id)

            csv_row = {}
            csv_row["first_name"] = reviewee["fields"]["First Name"][0]
            csv_row["last_name"] = reviewee["fields"]["Last Name"][0]
            csv_row["work_email"] = reviewee["fields"]["Lambda Email"][0]

            csv_row["function"] = ""
            csv_row["title"] = "Student"
            csv_row["level"] = ""

            # Make a new array without the reviewer
            reviewer_position = 1
            for reviewer_id in team_members:
                if reviewer_id != reviewee_id:
                    reviewer = peopledao.get_student(reviewer_id)

                    # Create the columns for the reviewers
                    csv_row["reviewer_first_name_" + str(reviewer_position)] = reviewer["fields"]["First Name"][0]
                    csv_row["reviewer_last_name_" + str(reviewer_position)] = reviewer["fields"]["Last Name"][0]
                    csv_row["reviewer_email_" + str(reviewer_position)] = reviewer["fields"]["Lambda Email"][0]

                    reviewer_position += 1

            print("{}".format(csv_row))
            peer_review_assignments.append(csv_row)

    with open("searchlight-export-" + event + "-" + time.strftime("%Y%m%d-%H%M%S") + ".csv", mode="w") as csv_file:
        fieldnames = ["first_name", "last_name", "work_email", "function", "title", "level"]
        for i in range(1, 15):
            fieldnames.append("reviewer_first_name_" + str(i))
            fieldnames.append("reviewer_last_name_" + str(i))
            fieldnames.append("reviewer_email_" + str(i))
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        writer.writeheader()

        for peer_review_assignment in peer_review_assignments:
            print("{}".format(peer_review_assignment))
            writer.writerow(peer_review_assignment)
