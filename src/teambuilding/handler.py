# Standard library imports
from collections import namedtuple
import math

# Local imports
from labsdao import people as peopledao
from labsdao import projects as projectsdao
from typing import Dict, List

USERNAME = "Labby"
ICON_URL = "https://labby-public-assets.s3.amazonaws.com/labby-small.png"

NOTIFICATION_DELAY_MINUTES = 5

HARDCODED_COHORT = "LabsPT10"

AssignmentTuple = namedtuple("Assignment", ["project", "student", "score"])

students: List[dict] = []
projects: List[dict] = []
assignments: List[AssignmentTuple] = []


def build_teams(event, context):
    global students, projects

    students = peopledao.get_all_student_surveys(HARDCODED_COHORT)
    print("Found {} students".format(len(students)))
    # for student in students:
    #     print("Student: {}\n".format(student))

    projects = projectsdao.get_all_active_projects(HARDCODED_COHORT)
    print("Found {} projects".format(len(projects)))

    while students:
        print("\n************************************************")
        print("Making pass with {} students left".format(len(students)))
        print("************************************************")

        best_assignment = __get_best_assignment()

        if best_assignment.project is None:
            print("!!! Unable to match students, dropping: {}", students.pop())
        else:
            project_name = best_assignment.project["fields"]["Name - Cohort"]
            student_name = best_assignment.student["fields"]["Student Name"][0]

            print(
                "\n== Assigning {} to project {} based on score: {}".format(
                    student_name, project_name, best_assignment.score
                )
            )

            assignments.append(best_assignment)

            students.remove(best_assignment.student)

        print("Remaining students: {}".format(len(students)))

    print("=================================================")
    print("Team assignments")
    print("=================================================")
    for assignment in assignments:
        __assign_to_project(assignment)


def __get_best_assignment() -> AssignmentTuple:
    scores: Dict[str, dict] = {}
    highscore = 0
    best_assignment = AssignmentTuple(None, None, None)

    print(
        "Finding best assignment for {} projects and {} students".format(
            len(projects), len(students)
        )
    )
    for project in projects:
        for student in students:
            print("==================================================================")

            project_name = project["fields"]["Name"]
            student_name = student["fields"]["Student Name"][0]
            print("Scoring {} - {}\n".format(project_name, student_name))

            # Create the dict for the student if it doesn't exist
            if project["id"] not in scores:
                scores[project["id"]] = {}

            score = __get_score(project, student)
            scores[project["id"]][student["id"]] = score

            print("\n")
            print("High Score: {}".format(highscore))
            print("Current Score: {}".format(score))

            # Don't assign a student to team if the score is really low
            if score > -5000:
                if best_assignment.project is None:
                    print(
                        "Starting high score: {} - {} = {}\n".format(
                            project_name, student_name, score
                        )
                    )
                    best_assignment = AssignmentTuple(project, student, score)
                    highscore = score
                elif score >= highscore:
                    print(
                        "New high score: {} - {} = {}\n".format(
                            project_name, student_name, score
                        )
                    )
                    best_assignment = AssignmentTuple(project, student, score)
                    highscore = score

            print("---\n")

    # print("Best Assignment: {} - {} = {}".format(best_assignment.student, best_assignment.project, score))

    return best_assignment


def __get_score(project: dict, student: dict) -> int:
    score = 0

    print(" == Track Scoring ==")
    project_name = project["fields"]["Name - Cohort"]
    student_name = student["fields"]["Student Name"][0]
    print("Scoring {} for project {}".format(student_name, project_name))

    project_tracks = project["fields"]["Program Names Text"]
    print("Project programs: {}".format(project_tracks))

    student_track = student["fields"]["Student Course Text"]
    print("Student Track: {}".format(student_track))

    if student_track not in project_tracks:
        print(
            "Student {} track not needed in project {}".format(
                student_name, project_name
            )
        )
        print("Track Score: {}".format(-10000))
        return -10000

    # print(" == Timezone Scoring ==")
    # tl_timezone = project['fields']['TL Timezone'][0]
    # student_timezone = student['fields']['What timezone are you in?']

    # print("Project timezone: {}".format(tl_timezone))
    # print("Student timezone: {}".format(student_timezone))

    # if student_timezone.upper() == tl_timezone.upper():
    #     print("Timezone Score: {}".format(1))
    #     score += 1

    print("\n== Team Size Scoring ==")
    team_size_score = __calculate_team_size_score(project, student)
    print("Adding team size score: {}".format(team_size_score))
    score += team_size_score

    print("\n== Team Compatibility Scoring ==")
    team_compatibilty_score = __calculate_team_compatibility_score(project, student)
    print("Adding team compatibility score: {}".format(team_compatibilty_score))
    score += team_compatibilty_score

    print("\n== Project Type Preference Scoring ==")
    project_type_preference_score = __calculate_project_type_preference_score(
        project, student
    )
    print(
        "Adding project type preference score: {}".format(project_type_preference_score)
    )
    score += project_type_preference_score

    WEB_TIER_FOCUS_FIELD = "Where do you most prefer spending your time coding?"
    print("\n== {} ==".format(WEB_TIER_FOCUS_FIELD))
    web_focus_score = __calculate_score_for_average_goal(
        project, student, WEB_TIER_FOCUS_FIELD, 3.00, 5
    )
    print("Adding score: {}".format(web_focus_score))
    score += web_focus_score

    WEB_DATA_MODELING_FIELD = "How comfortable are you at web design?"
    print("\n== {} ==".format(WEB_DATA_MODELING_FIELD))
    web_data_modeling_score = __calculate_score_for_average_goal(
        project, student, WEB_DATA_MODELING_FIELD, 3.00, 5
    )
    print("Adding score: {}".format(web_data_modeling_score))
    score += web_data_modeling_score

    WEB_DESIGN_FIELD = "How comfortable are you at web design?"
    print("\n== {} ==".format(WEB_DESIGN_FIELD))
    web_design_score = __calculate_score_for_average_goal(
        project, student, WEB_DESIGN_FIELD, 3.00, 5
    )
    print("Adding score: {}".format(web_design_score))
    score += web_design_score

    DATA_MODELING_CONFIDENCE = "How comfortable are you at data modeling?"
    print("\n== {} ==".format(DATA_MODELING_CONFIDENCE))
    data_model_confidence_score = __calculate_score_for_average_goal(
        project, student, DATA_MODELING_CONFIDENCE, 3.00, 5
    )
    print("Adding score: {}".format(data_model_confidence_score))
    score += data_model_confidence_score

    ASSERTIVENESS = "How often do you speak up during group discussions?"
    print("\n== {} ==".format(ASSERTIVENESS))
    assertiveness_score = __calculate_score_for_average_goal(
        project, student, ASSERTIVENESS, 3.00, 5
    )
    print("Adding score: {}".format(assertiveness_score))
    score += assertiveness_score

    PLANNING = "Do you plan ahead or play it by ear?"
    print("\n== {} ==".format(PLANNING))
    planning_score = __calculate_score_for_average_goal(
        project, student, PLANNING, 3.00, 5
    )
    print("Adding score: {}".format(planning_score))
    score += planning_score

    VISION = "Are you more interested in the big picture or details?"
    print("\n== {} ==".format(VISION))
    vision_score = __calculate_score_for_average_goal(project, student, VISION, 3.00, 5)
    print("Adding score: {}".format(vision_score))
    score += vision_score

    return score


def __calculate_project_type_preference_score(project: dict, student: dict) -> int:
    project_name = project["fields"]["Name - Cohort"]
    student_name = student["fields"]["Student Name"][0]

    # Can't generate a score if project has no category
    if "Category" not in project["fields"]:
        raise Exception("Project {} has no category!".format(project_name))

    project_category = project["fields"]["Category"][0]

    # Student has no preference
    if (
        "If you have a preference, please choose up to 3 types of product you would like to contribute to:"
        not in student["fields"]
    ):
        print(
            "Student {} has no category preferences, so no score".format(student_name)
        )
        return 0

    student_category_preferences = student["fields"][
        "If you have a preference, please choose up to 3 types of product you would like to contribute to:"
    ]
    print(
        "Student {} has category preferences: {}".format(
            student_name, student_category_preferences
        )
    )

    for student_category_preference in student_category_preferences:
        if project_category.upper() in student_category_preference.upper():
            print(
                "Student has matching category preference ({}) so score is 100".format(
                    student_category_preference
                )
            )
            return 100

    print(
        "No matching student category preferences ({}) for project category ({}) so score is -100".format(
            student_category_preferences, project_category
        )
    )
    return -100


def __calculate_team_size_score(project: dict, student: dict) -> int:
    student_track = student["fields"]["Student Course Text"]

    average_team_size = __get_average_team_size(student_track)
    print("Current average team size: {}".format(average_team_size))

    project_name = project["fields"]["Name - Cohort"]

    team_member_count = __count_team_assignments(project, student_track)
    print(
        "Project {} has {} members in track {} with {} being the average for that track".format(
            project_name, team_member_count, student_track, average_team_size
        )
    )

    score = math.ceil(100 * (average_team_size - team_member_count))

    return score


def __get_average_team_size(track: str) -> float:
    assignments_for_track = []
    for assignment in assignments:
        if assignment.student["fields"]["Student Course Text"].upper() == track.upper():
            assignments_for_track.append(assignment)

    number_of_assignments = len(assignments_for_track)

    teams_requiring_track = []
    for project in projects:
        if track.upper() in project["fields"]["Program Names Text"].upper():
            teams_requiring_track.append(project)

    number_of_teams = len(teams_requiring_track)

    print(
        "Averaging number of assignments {} with number of teams {}".format(
            number_of_assignments, number_of_teams
        )
    )
    average_team_size = float(number_of_assignments) / float(number_of_teams)

    return average_team_size


def __calculate_score_for_average_goal(
    project: dict, student: dict, survey_field: str, desired_average: float, weight: int
) -> int:
    project_name = project["fields"]["Name - Cohort"]
    student_name = student["fields"]["Student Name"][0]

    print(
        "Calculating score for: Project({}) - Student({}) - Field({}) - Desired Average({})".format(
            project_name, student_name, survey_field, desired_average
        )
    )

    # Check to see if the student responded to the survey, question
    if survey_field not in student["fields"]:
        # If not, this has no effect on the score
        return 0

    # Get the list of current assignments for the project team
    team_assignments = __get_team_assignments(project)

    # Calculate the average response to the question for the current assignments; ignore blank responses
    number_of_responses = 0
    sum_of_responses = 0
    for assignment in team_assignments:
        # Only consider assignments with a response to the survey question
        if survey_field in assignment.student["fields"]:
            number_of_responses += 1
            sum_of_responses += assignment.student["fields"][survey_field]

    # Calculate the average response
    team_response_average = 0.00

    # If there are currently no responses, the students answer becomes the average
    if number_of_responses == 0:
        # If no responses yet, assume the desired average is the average
        team_response_average = desired_average
    else:
        # Calculate the average response from the current assignments
        team_response_average = sum_of_responses / number_of_responses

    # This is the response from the student
    student_response = student["fields"][survey_field]

    # The score is based on trying to pull the team average toward the desired average
    score = 0
    if (
        team_response_average > desired_average
        and student_response < team_response_average
    ):
        # Yes, we want this student on the team. The team average is higher than desired and they'll pull the average down.
        score = weight
    elif (
        team_response_average > desired_average
        and student_response > team_response_average
    ):
        # No, we don't want this student on the team. The team average is higher than desired and they'll push the average up.
        score = -weight
    elif (
        team_response_average < desired_average
        and student_response > team_response_average
    ):
        # Yes, we want this student on the team. The team average is lower than desired and they'll push the average up.
        score = weight
    elif (
        team_response_average < desired_average
        and student_response < team_response_average
    ):
        # No, we don't want this student on the team. The team average is lower than desired and they'll pull the average down.
        score = -weight

    print(
        "Score: {} (Based on team average {} and student response {})".format(
            score, team_response_average, student_response
        )
    )

    # Note the score may be zero
    return score


def __calculate_team_compatibility_score(project: dict, student: dict) -> int:
    project_name = project["fields"]["Name - Cohort"]
    student_name = student["fields"]["Student Name"][0]

    print(
        "Calculating compatibility score for: Project({}) - Student({})".format(
            project_name, student_name
        )
    )

    # Check to see if the student responded to the survey, question
    # print(student['fields'])
    if "Incompatible Student Names" not in student["fields"]:
        # If not, this has no effect on the score
        return 0

    student_not_compatible_list = student["fields"]["Incompatible Student Names"]
    print(
        "Checking incompatibility list for student {}: {}".format(
            student_name, student_not_compatible_list
        )
    )

    # Get the list of current assignments for the project team
    team_assignments = __get_team_assignments(project)

    for assignment in team_assignments:
        assigned_student_name = assignment.student["fields"]["Student Name"][0]

        print(
            "Checking to see if {} in {}".format(
                assigned_student_name, student_not_compatible_list
            )
        )
        if assigned_student_name in student_not_compatible_list:
            print(
                "*** Student {} says they don't want to work with one of ({}), who are already assigned to project {}".format(
                    student_name, student_not_compatible_list, project_name
                )
            )

            # Definitely not a good fit for the team
            return -100000

        # print(assignment.student['fields'])
        if "Incompatible Students Names" in assignment.student["fields"]:
            for incompatibleStudent in assignment.student["fields"][
                "Incompatible Student Names"
            ]:
                if student_name.upper() == incompatibleStudent.upper():
                    print(
                        "*** Assigned student {} says they don't want to work with {} one of whom is assigned to project {}".format(
                            assigned_student_name, student_name, project_name
                        )
                    )

                    # Definitely not a good fit for the team
                    return -100000

    return 0


def __get_team_assignments(project: dict) -> List[AssignmentTuple]:
    global assignments

    team_assignments: List[AssignmentTuple] = []
    for assignment in assignments:
        if assignment.project["id"] == project["id"]:
            team_assignments.append(assignment)

    return team_assignments


def __count_team_assignments(project: dict, track: str) -> float:
    number_of_assignments = 0
    for assignment in assignments:
        if assignment.project["id"] == project["id"]:
            if (
                assignment.student["fields"]["Student Course Text"].upper()
                == track.upper()
            ):
                number_of_assignments += 1

    return number_of_assignments


def __assign_to_project(assignment: AssignmentTuple):
    # print("{}".format(assignment))

    projectsdao.assign_student_to_project(
        assignment.student, assignment.project, assignment.score
    )
