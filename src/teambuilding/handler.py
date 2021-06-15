# Standard library imports
from collections import Counter, namedtuple
import math
from typing import Dict, List

# Local imports
from labsdao import people as peopledao
from labsdao import projects as projectsdao

BAD_FIT_SCORE = -100000

TEAM_SIZE_WEIGHT = 200

SURVEY_STUDENT_NAME_FIELD = "Student Name"
SURVEY_PRODUCT_OPT_OUT_FIELD = "Product Opt Out Text"

SURVEY_ETHNICITIES_FIELD = "Ethnicities"
SURVEY_BASE_ETHNICITY_WEIGHT = 250

SURVEY_GENDER_FIELD = "Gender"
SURVEY_GENDER_BASE_WEIGHT = 750

SURVEY_TRACK_FIELD = "Track"
SURVEY_INCOMPATIBLE_STUDENT_NAMES_FIELD = "Incompatible Student Names"

PROJECT_NAME_FIELD = "Name"
PROJECT_PRODUCT_NAME_FIELD = "Product Name"
PROJECT_TRACKS_FIELD = "Tracks"

SURVEY_ASSERTIVENESS_FIELD = "How often do you speak up during group discussions?"
SURVEY_ASSERTIVENESS_WEIGHT = 50

SURVEY_PLANNING_FIELD = "Do you plan ahead or play it by ear?"
SURVEY_PLANNING_WEIGHT = 50

SURVEY_VISION_FIELD = "Are you more interested in the big picture or details?"
SURVEY_VISION_WEIGHT = 50

SURVEY_FRONTEND_FIELD = "How comfortable are you working on the frontend?"
SURVEY_FRONTEND_WEIGHT = 100

SURVEY_WEB_DESIGN_FIELD = "How comfortable are you at web design?"
SURVEY_WEB_DESIGN_WEIGHT = 100

SURVEY_DATA_MODELING_FIELD = "How comfortable are you at data modeling?"
SURVEY_DATA_MODELING_WEIGHT = 100

SURVEY_UX_INTEREST_FIELD = "UX Interest"
SURVEY_UX_INTEREST_WEIGHT = 200

SURVEY_GIT_FIELD = "Git Expertise"
SURVEY_GIT_WEIGHT = 100

SURVEY_DOCKER_FIELD = "Docker Expertise"
SURVEY_DOCKER_WEIGHT = 100

SURVEY_STUDENT_TIMEZONE_FIELD = "Student Timezone Offset"
SURVEY_STUDENT_TIMEZONE_WEIGHT = 150

AssignmentTuple = namedtuple("Assignment", ["project", "student", "score"])


def build_teams(event, context):
    """Main AWS Lambda handeler function that orchestrates the calculation.

    Parameters:
        event -- AWS Lambda event
        context -- AWS Lambda context

    Returns:
        Nothing
    """
    if not event:
        raise ("You must provide the cohort ID as data in the event")

    surveys: List[dict] = []
    projects: List[dict] = []
    assignments: List[AssignmentTuple] = []

    # Use the DAO to grab the list of all of the surveys
    unassigned_students = peopledao.get_all_student_surveys(event)

    # Sort the incoming surveys to help the algorithm produce the best results
    # Note: Can't have just one of the element reverse sorted, so must to multiple sorts
    #       Multiple sorts must be performed _least_ significant to _most_
    unassigned_students.sort(
        key=lambda survey: (str(survey["fields"].get(SURVEY_TRACK_FIELD, ""))),
        reverse=False,
    )
    unassigned_students.sort(
        key=lambda survey: (str(survey["fields"].get(SURVEY_PRODUCT_OPT_OUT_FIELD, ""))),
        reverse=True,
    )
    unassigned_students.sort(
        key=lambda survey: (str(survey["fields"].get(SURVEY_ETHNICITIES_FIELD, ""))),
        reverse=False,
    )
    unassigned_students.sort(
        key=lambda survey: (str(survey["fields"].get(SURVEY_GENDER_FIELD, ""))),
        reverse=True,
    )

    projects = projectsdao.get_all_active_projects(event)

    while surveys:
        best_assignment = _get_best_assignment(projects, assignments, unassigned_students)

        if best_assignment.project is None:
            print("\n")
            print("*" * 120)
            print("!!!Unable to match student: {}", unassigned_students.pop())
            print("*" * 120)
        else:
            assignments.append(best_assignment)

            unassigned_students.remove(best_assignment.student)

    print("\n")
    print("=" * 120)
    print("Team assignments")
    print("=" * 120)

    # This sorting is just so they display nicely in the output
    assignments.sort(
        key=lambda x: (
            x[0]["fields"].get(PROJECT_NAME_FIELD),
            x[1]["fields"].get(SURVEY_TRACK_FIELD),
            x[1]["fields"].get(SURVEY_GENDER_FIELD, ""),
            str(x[1]["fields"].get(SURVEY_ETHNICITIES_FIELD, "")),
        )
    )

    # Output the final assignments and write them to the DAO
    TABLE_FORMAT_STRING = "{:<35} {:>6} {:<30} {:<85} {:<55} {:>5}"

    print(
        TABLE_FORMAT_STRING.format(
            "Project",
            SURVEY_TRACK_FIELD,
            "Gender",
            "Ethnicities",
            "Opt Out",
            "TZ",
        )
    )

    print("=" * 120)

    for assignment in assignments:
        print(
            TABLE_FORMAT_STRING.format(
                assignment.project["fields"][PROJECT_NAME_FIELD],
                assignment.student["fields"][SURVEY_TRACK_FIELD],
                assignment.student["fields"].get(SURVEY_GENDER_FIELD, "-"),
                str(assignment.student["fields"].get(SURVEY_ETHNICITIES_FIELD, list("-"))).strip("[]"),
                str(assignment.student["fields"].get("Product Opt Out Text", list("-"))).strip("[]"),
                assignment.student["fields"].get(SURVEY_STUDENT_TIMEZONE_FIELD, "-"),
            )
        )

        # This actually writes the teams to the DAO
        projectsdao.assign_student_to_project(assignment.student, assignment.project, assignment.score)


def _get_best_assignment(
    projects: List[dict], assignments: List[AssignmentTuple], students: List[AssignmentTuple]
) -> AssignmentTuple:
    """Find the highest scoring assignment given a set of projects, assigned and unassigned students

    Args:
        projects (List[dict]): [description]
        assignments (List[AssignmentTuple]): [description]
        students (List[AssignmentTuple]): [description]

    Returns:
        AssignmentTuple: [description]
    """
    scores: Dict[str, dict] = {}
    highscore = 0
    best_assignment = AssignmentTuple(None, None, None)
    for project in projects:
        for student in students:
            score = _get_score(projects, assignments, project, student)
            scores[project["id"]] = {student["id"]: score}

            # Don't assign a student to team if the score is really low
            if score > -5000:
                if best_assignment.project is None:
                    best_assignment = AssignmentTuple(project, student, score)
                    highscore = score
                elif score >= highscore:
                    best_assignment = AssignmentTuple(project, student, score)
                    highscore = score

    return best_assignment


def _get_score(projects: List[dict], assignments: List[AssignmentTuple], project: dict, student: dict) -> int:
    score = 0

    # =======================================================================================
    # Match student track to project required track
    # =======================================================================================
    project_tracks_upper = [track.upper() for track in project["fields"][PROJECT_TRACKS_FIELD]]
    student_track_upper = student["fields"].get(SURVEY_TRACK_FIELD, "").upper()

    if student_track_upper not in project_tracks_upper:
        return BAD_FIT_SCORE

    # =========================================================================
    # Returns a score reflecting how far this student will push team size from
    # the average
    # =========================================================================
    team_size_score = _calculate_team_size_score(projects, assignments, project, student)
    score += team_size_score

    # =======================================================================================
    # Returns a score reflecting how compatible the student is with other team members
    # =======================================================================================
    # print("\n== Team Compatibility Scoring ==")
    team_compatibility_score = _calculate_student_to_team_compatibility_score(assignments, project, student)
    # print("Adding team compatibility score: {}".format(team_compatibility_score))
    score += team_compatibility_score

    # =======================================================================================
    # These calculations prefer the creation of diverse teams
    # =======================================================================================
    # print("\n== Ethnic Diversity Scoring ==")
    ethnic_diversity_score = _calculate_ethnic_diversity_score(assignments, project, student)
    # print("Adding ethnic diversity score: {}".format(ethnic_diversity_score))
    score += ethnic_diversity_score

    # print("\n== Gender Diversity Scoring ==")
    gender_diversity_score = _calculate_gender_diversity_score(assignments, project, student)
    # print("Adding gender diversity score: {}".format(gender_diversity_score))
    score += gender_diversity_score

    # =======================================================================================
    # Align team members by timezone
    # =======================================================================================
    # print("\n== {} ==".format(SURVEY_STUDENT_TIMEZONE_FIELD))
    timezone_score = _calculate_score_for_average_goal(
        assignments,
        project,
        student,
        SURVEY_STUDENT_TIMEZONE_FIELD,
        3.00,
        SURVEY_STUDENT_TIMEZONE_WEIGHT,
    )
    score += timezone_score

    # =======================================================================================
    # These calculations try to force the team to average particular skills/traits
    # =======================================================================================
    # print("\n== {} ==".format(UX_INTEREST_FIELD))
    ux_interest_score = _calculate_score_for_average_goal(
        assignments,
        project,
        student,
        SURVEY_UX_INTEREST_FIELD,
        3.00,
        SURVEY_UX_INTEREST_WEIGHT,
    )
    score += ux_interest_score

    # print("\n== {} ==".format(SURVEY_GIT_FIELD))
    git_expertise_score = _calculate_score_for_average_goal(
        assignments,
        project,
        student,
        SURVEY_GIT_FIELD,
        3.00,
        SURVEY_GIT_WEIGHT,
    )
    score += git_expertise_score

    # print("\n== {} ==".format(SURVEY_DOCKER_FIELD))
    docker_expertise_score = _calculate_score_for_average_goal(
        assignments,
        project,
        student,
        SURVEY_DOCKER_FIELD,
        3.00,
        SURVEY_DOCKER_WEIGHT,
    )
    score += docker_expertise_score

    # print("\n== {} ==".format(SURVEY_FRONTEND_FIELD))
    web_focus_score = _calculate_score_for_average_goal(
        assignments,
        project,
        student,
        SURVEY_FRONTEND_FIELD,
        3.00,
        SURVEY_FRONTEND_WEIGHT,
    )
    score += web_focus_score

    # print("\n== {} ==".format(SURVEY_DATA_MODELING_FIELD))
    web_data_modeling_score = _calculate_score_for_average_goal(
        assignments,
        project,
        student,
        SURVEY_DATA_MODELING_FIELD,
        3.00,
        SURVEY_DATA_MODELING_WEIGHT,
    )
    score += web_data_modeling_score

    # print("\n== {} ==".format(SURVEY_WEB_DESIGN_FIELD))
    web_design_score = _calculate_score_for_average_goal(
        assignments,
        project,
        student,
        SURVEY_WEB_DESIGN_FIELD,
        3.00,
        SURVEY_WEB_DESIGN_WEIGHT,
    )
    score += web_design_score

    # print("\n== {} ==".format(SURVEY_ASSERTIVENESS_FIELD))
    assertiveness_score = _calculate_score_for_average_goal(
        assignments,
        project,
        student,
        SURVEY_ASSERTIVENESS_FIELD,
        3.00,
        SURVEY_ASSERTIVENESS_WEIGHT,
    )
    score += assertiveness_score

    # print("\n== {} ==".format(SURVEY_PLANNING_FIELD))
    planning_score = _calculate_score_for_average_goal(
        assignments,
        project,
        student,
        SURVEY_PLANNING_FIELD,
        3.00,
        SURVEY_PLANNING_WEIGHT,
    )
    score += planning_score

    # print("\n== {} ==".format(SURVEY_VISION_FIELD))
    vision_score = _calculate_score_for_average_goal(
        assignments, project, student, SURVEY_VISION_FIELD, 3.00, SURVEY_VISION_WEIGHT
    )
    score += vision_score

    return score


def _calculate_team_size_score(
    projects: List[dict], assignments: List[AssignmentTuple], project: dict, student: dict
) -> int:
    """Calculates the weighted score based on how far away from the average team size this project would
       be after assigning the student

    Args:
        projects (List[dict]): All of the projects
        assignments (List[AssignmentTuple]): All of the current assignments
        project (dict): The project the student is being scored for
        student (dict): The student being scored

    Returns:
        int: A score representing how far the project size would be from the average
    """
    student_track = student["fields"][SURVEY_TRACK_FIELD]

    # Calculate the current average team size for this track
    average_team_size = _get_average_team_size_for_track(projects, assignments, student_track)

    # Calculate the current size of the team for the track
    project_team_member_count = sum(
        assignment.project["fields"]["id"] == project["fields"]["id"]
        and assignment.student["fields"][SURVEY_TRACK_FIELD] == student_track
        for assignment in assignments
    )

    score = math.ceil(TEAM_SIZE_WEIGHT * (average_team_size - project_team_member_count))

    return score


def _get_average_team_size_for_track(projects: List[dict], assignments: List[AssignmentTuple], track: str) -> float:
    """Calculates the average team size for a particular track by dividing the number of assignments for the track
       by the total number of projects requiring that track.

       e.g. If 4 projects require DS track students and 8 DS students have been assigned:
         DS Assignments/DS Projects = 8/4 = 2

    Args:
        projects (List[dict]): All of the projects
        assignments (List[AssignmentTuple]): All of the current assignments
        track (str): The specific track to find the average for

    Returns:
        float: The average number of assignments for the track
    """
    # How many assignments have been made for the specified track?
    number_of_assignments_for_track = sum(
        track == assignment.student["fields"][SURVEY_TRACK_FIELD] for assignment in assignments
    )

    # Filter the list of projects down to only those requiring the track
    number_of_teams_requiring_track = sum(track in project["fields"][PROJECT_TRACKS_FIELD] for project in projects)

    average_team_size = float(number_of_assignments_for_track) / float(number_of_teams_requiring_track)

    return average_team_size


def _calculate_score_for_average_goal(
    assignments: List[AssignmentTuple],
    project: dict,
    student: dict,
    survey_field: str,
    desired_average: float,
    weight: int,
) -> int:
    # Check to see if the student responded to the survey, question
    if survey_field not in student["fields"]:
        # If not, this has no effect on the score
        return 0

    # Get the list of current assignments for the project team
    team_assignments = filter(lambda assignment: assignment.project["id"] == project["id"], assignments)

    # Calculate the average response to the question for the current assignments;
    # ignore blank responses
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
    if team_response_average > desired_average and student_response < team_response_average:
        # Yes, we want this student on the team. The team average is higher than
        # desired and they'll pull the average down.
        score = weight
    elif team_response_average > desired_average and student_response > team_response_average:
        # No, we don't want this student on the team. The team average is higher than
        # desired and they'll push the average up.
        score = -weight
    elif team_response_average < desired_average and student_response > team_response_average:
        # Yes, we want this student on the team. The team average is lower than desired
        # and they'll push the average up.
        score = weight
    elif team_response_average < desired_average and student_response < team_response_average:
        # No, we don't want this student on the team. The team average is lower than
        # desired and they'll pull the average down.
        score = -weight

    # Note the score may be zero
    return score


def _calculate_student_to_team_compatibility_score(
    assignments: List[AssignmentTuple], project: dict, student_to_score: dict
) -> int:
    """Returns a score representing the student's compatibility with students already assigned to project

    Args:
        assignments (List[AssignmentTuple]): The current list of student/project assignments
        project (dict): The project to score the student against
        student_to_score (dict): The student being scored

    Returns:
        int: 0 if the student is compatible; BAD_FIT_SCORE if the student is not compatible
    """
    # This is the student we're scoring
    student_name = student_to_score["fields"][SURVEY_STUDENT_NAME_FIELD][0]

    # Get the list of current assignments for the project team we're calculating the score for
    team_assignments = filter(
        lambda assignment: assignment.project["fields"]["id"] == project["fields"]["id"], assignments
    )

    # Go through each assignment to be sure the student being checked _and_ the already assigned students are compatible
    for assignment in team_assignments:
        # Check to see if the student we're scoring lists any other students as incompatible
        if SURVEY_INCOMPATIBLE_STUDENT_NAMES_FIELD in student_to_score["fields"]:
            student_not_compatible_list = student_to_score["fields"][SURVEY_INCOMPATIBLE_STUDENT_NAMES_FIELD]

            # Get the name of the currently assigned student
            assigned_student_name = assignment.student["fields"][SURVEY_STUDENT_NAME_FIELD][0]

            # See if the student we're scoring listed the assigned student as incompatible
            if assigned_student_name in student_not_compatible_list:

                # If so, this student gets a really low score for this team
                return BAD_FIT_SCORE

        # Check whether the currently assigned student lists the student being scored as incompatible
        if SURVEY_INCOMPATIBLE_STUDENT_NAMES_FIELD in assignment.student["fields"]:
            assigned_student_not_compatible_list = assignment.student["fields"][SURVEY_INCOMPATIBLE_STUDENT_NAMES_FIELD]

            # See if the student we're scoring is listed by the assigned student as incompatible
            if student_name in assigned_student_not_compatible_list:

                # If so, this student gets a really low score for this team
                return BAD_FIT_SCORE

    return 0


def _calculate_ethnic_diversity_score(assignments: List[AssignmentTuple], project: dict, student: dict) -> int:
    """Calculates a score that indicates if this student will complete a ethnic pair
    on the team. This will try to always have at least 2 people who share the same
    ethnic identity on the same team.

    Parameters:
        project -- The project
        student -- The student

    Returns:
        A score
    """
    # Get the ethnicities specified by the student
    student_ethnicities = student["fields"].get(SURVEY_ETHNICITIES_FIELD, None)
    if not student_ethnicities:
        # The student didn't specify ethnicities, so we can't calculate a score
        return 0

    # Get the list of current assignments for the project team
    team_assignments = filter(
        lambda assignment: assignment.project["fields"]["id"] == project["fields"]["id"], assignments
    )

    # This list will hold the list of ethnicities on the team
    team_ethnicities = []
    for assignment in team_assignments:
        assigned_student_ethnicities = assignment.student["fields"].get(SURVEY_ETHNICITIES_FIELD, None)

        if assigned_student_ethnicities:
            team_ethnicities.append(assigned_student_ethnicities)

    # Team ethnicities is going to be a list of lists, so let's flatten it
    team_ethnicities = [item for sublist in team_ethnicities for item in sublist]

    # ================================================================================================================
    # Get the count ethnicities for the already assigned students
    ethnicity_counter = Counter(team_ethnicities)

    # Check each of the student's listed ethnicities and take the highest score
    best_ethnicity_score = 0
    for student_ethnicity in student_ethnicities:
        matching_ethnicity_count = ethnicity_counter.get(student_ethnicity, 0)

        current_ethnicity_score = 0

        if matching_ethnicity_count == 0:
            # This is good, as it will make the team more diverse
            current_ethnicity_score = SURVEY_BASE_ETHNICITY_WEIGHT
        elif matching_ethnicity_count == 1:
            # This is better, as it will pair students with like ethnicities
            current_ethnicity_score = SURVEY_BASE_ETHNICITY_WEIGHT * 2

        # Check to see if this is a better match
        if current_ethnicity_score > best_ethnicity_score:
            best_ethnicity_score = current_ethnicity_score

    return best_ethnicity_score


def _calculate_gender_diversity_score(assignments: List[AssignmentTuple], project: dict, student: dict) -> int:
    """Calculates a score that indicates if this student will complete a gender pair
    on the team. This will try to always have at least 2 people who share the same
    gender identity on the same team.

    Parameters:
        project -- The project
        student -- The student

    Returns:
        A score
    """
    # Get the gender specified by the student
    student_gender = student["fields"].get(SURVEY_GENDER_FIELD, None)
    if not student_gender:
        # The student didn't provide a gender, so we can't calculate a score
        return 0

    # Get the list of current assignments for the project team
    team_assignments = filter(
        lambda assignment: assignment.project["fields"]["id"] == project["fields"]["id"], assignments
    )

    # This list will hold the list of genders on the team
    team_genders = []
    for assignment in team_assignments:
        assigned_student_gender = assignment.student["fields"].get(SURVEY_GENDER_FIELD, None)

        if assigned_student_gender:
            team_genders.append(assigned_student_gender)

    # ================================================================================================================
    # Get the count genders for the already assigned students
    gender_counter = Counter(team_genders)

    # Get the count of the particular gender that matches the student
    matching_gender_count = gender_counter.get(student_gender, 0)

    if matching_gender_count == 0:
        # This is good, as it will make the team more diverse
        return SURVEY_GENDER_BASE_WEIGHT
    elif matching_gender_count == 1:
        # This is better, as it will pair students with like genders
        return SURVEY_GENDER_BASE_WEIGHT * 2
    else:
        # There are already at least 2 student with this gender identity, so we won't
        # prefer this
        return 0
