# Standard library imports
import csv
import time

# Local imports
from ..labsdao import projects as projectsdao
from ..labsdao import people as peopledao


def generate_labs_reviewer_csv(event, context):
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

            # The data sometimes is missing the student's email address
            csv_row["work_email"] = reviewee["fields"].get("Lambda Email", ["MISSING EMAIL"])[0]

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

                    # The data sometimes is missing the student's email address
                    csv_row["reviewer_email_" + str(reviewer_position)] = reviewer["fields"].get(
                        "Lambda Email", ["MISSING EMAIL"]
                    )[0]

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


def generate_bw_reviewer_csv(event, context):
    """Generates a CSV file with all required reviews for BW track teams

    Parameters:
        event -- String indicating the BW section to process: FT, PTPT, PTCT
        context -- Not used

    Returns:
        Nothing
    """
    if not event:
        raise ("You must provide the Section as data in the event. One of: FT, PTPT, PTCT")

    # Use the DAO to grab the list of all active projects
    student_records = peopledao.get_all_bw_students(event)
    print("Found {} student records".format(len(student_records)))

    # Use a Lambda function to filter the metadata from the records
    students = list(map(lambda student: student["fields"], student_records))

    # Organize the students into track teams
    track_teams = {}
    for student in students:
        track_team_id = student["Active Track Team"][0]

        if track_team_id not in track_teams.keys():
            track_teams[track_team_id] = [student]
        else:
            track_teams[track_team_id].append(student)

    peer_review_assignments = []
    for track_team, team_members in track_teams.items():
        print("\n")
        print("Processing Track Team: {}".format(track_team))
        print("Team Members: {}".format(team_members))

        for i in range(0, len(team_members)):
            reviewee = team_members[i]

            csv_row = {}
            csv_row["first_name"] = reviewee["First Name"][0]
            csv_row["last_name"] = reviewee["Last Name"][0]
            csv_row["work_email"] = reviewee["Lambda Email"][0]
            csv_row["team"] = reviewee["Active Track Team"][0]

            csv_row["function"] = ""
            csv_row["title"] = "Student"
            csv_row["level"] = ""

            # Make a new array without the reviewer
            reviewer_position = 1
            for team_member in team_members:
                if team_member["Lambda Email"][0] != reviewee["Lambda Email"][0]:
                    # Create the columns for the reviewers
                    csv_row["reviewer_first_name_" + str(reviewer_position)] = team_member["First Name"][0]
                    csv_row["reviewer_last_name_" + str(reviewer_position)] = team_member["Last Name"][0]
                    csv_row["reviewer_email_" + str(reviewer_position)] = team_member["Lambda Email"][0]

                    reviewer_position += 1

            print("{}".format(csv_row))
            peer_review_assignments.append(csv_row)

    with open("searchlight-export-bw-" + event + "-" + time.strftime("%Y%m%d-%H%M%S") + ".csv", mode="w") as csv_file:
        fieldnames = ["first_name", "last_name", "work_email", "team", "function", "title", "level"]
        for i in range(1, 15):
            fieldnames.append("reviewer_first_name_" + str(i))
            fieldnames.append("reviewer_last_name_" + str(i))
            fieldnames.append("reviewer_email_" + str(i))
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        writer.writeheader()

        for peer_review_assignment in peer_review_assignments:
            print("{}".format(peer_review_assignment))
            writer.writerow(peer_review_assignment)
