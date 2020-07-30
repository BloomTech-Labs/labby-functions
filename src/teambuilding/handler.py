# Standard library imports
from collections import Counter, namedtuple
import math

# Local imports
from ..labsdao import people as peopledao
from ..labsdao import projects as projectsdao
from typing import Dict, List

HARDCODED_COHORT = "Labs25"

STUDENT_TABLE_NAME_FIELD = "Student Name"
STUDENT_TABLE_TRACK_FIELD = "Student Course Text"
STUDENT_TABLE_INCOMPATIBLE_STUDENT_NAMES_FIELD = "Incompatible Student Names"

PROJECT_TABLE_NAME_FIELD = "Name"
PROJECT_TABLE_PRODUCT_NAME_FIELD = "Product Name"
PROJECT_TABLE_PROGRAMS_FIELD = "Programs Text"

SURVEY_TABLE_ASSERTIVENESS_FIELD = "How often do you speak up during group discussions?"
SURVEY_TABLE_PLANNING_FIELD = "Do you plan ahead or play it by ear?"

SURVEY_TABLE_FRONTEND_FIELD = "How comfortable are you working on the frontend?"
SURVEY_TABLE_FRONTEND_WEIGHT = 10

SURVEY_TABLE_WEB_DESIGN_FIELD = "How comfortable are you at web design?"
SURVEY_TABLE_WEB_DESIGN_WEIGHT = 5

SURVEY_TABLE_DATA_MODELING_FIELD = "How comfortable are you at data modeling?"
SURVEY_TABLE_DATA_MODELING_WEIGHT = 5

SURVEY_STUDENT_TIMEZONE_FIELD = "Student Timezone Offset"
SURVEY_STUDENT_TIMEZONE_WEIGHT = 5

SURVEY_TABLE_PRODUCT_OPT_OUT_FIELD = "Product Opt Out Text"
SURVEY_TABLE_ETHNICITIES_FIELD = "Ethnicities"
SURVEY_TABLE_GENDER_FIELD = "Gender"

SCORE_WEIGHT_TEAM_SIZE = 200

AssignmentTuple = namedtuple("Assignment", ["project", "student", "score"])

students: List[dict] = []
projects: List[dict] = []
assignments: List[AssignmentTuple] = []


def build_teams(event, context):
    global students, projects

    students = peopledao.get_all_student_surveys(HARDCODED_COHORT)
    print("Found {} students".format(len(students)))

    projects = projectsdao.get_all_active_projects(HARDCODED_COHORT)
    print("Found {} projects".format(len(projects)))

    while students:
        print("\n")
        print("*" * 120)
        print("Making pass with {} students left".format(len(students)))
        print("*" * 120)

        best_assignment = __get_best_assignment()

        if best_assignment.project is None:
            print("\n")
            print("*" * 120)
            print("!!!Unable to match student: {}", students.pop())
            print("*" * 120)
        else:
            project_name = best_assignment.project["fields"][PROJECT_TABLE_NAME_FIELD]
            student_name = best_assignment.student["fields"][STUDENT_TABLE_NAME_FIELD][
                0
            ]

            print("\n")
            print("*" * 120)
            print(
                "Assigning {} to project {} based on score: {}".format(
                    student_name, project_name, best_assignment.score
                )
            )
            print("*" * 120)

            assignments.append(best_assignment)

            students.remove(best_assignment.student)

    print("\n")
    print("=" * 120)
    print("Team assignments")
    print("=" * 120)

    # This sorting is just so they display nicely in the output
    assignments.sort(
        key=lambda x: (
            x[0]["fields"].get(PROJECT_TABLE_NAME_FIELD),
            x[1]["fields"].get(STUDENT_TABLE_TRACK_FIELD),
            x[1]["fields"].get(SURVEY_TABLE_GENDER_FIELD, ""),
            str(x[1]["fields"].get(SURVEY_TABLE_ETHNICITIES_FIELD, "")),
        )
    )

    # Output the final assignments and write them to the DAO
    TABLE_FORMAT_STRING = "{:<35} {:>6} {:<30} {:<70} {:<55} {:>5}"

    print(
        TABLE_FORMAT_STRING.format(
            "Project", "Track", "Gender", "Ethnicities", "Opt Out", "TZ"
        )
    )

    print("=" * 120)

    for assignment in assignments:
        print(
            TABLE_FORMAT_STRING.format(
                assignment.project["fields"][PROJECT_TABLE_NAME_FIELD],
                assignment.student["fields"][STUDENT_TABLE_TRACK_FIELD],
                assignment.student["fields"].get(SURVEY_TABLE_GENDER_FIELD, "-"),
                str(
                    assignment.student["fields"].get(
                        SURVEY_TABLE_ETHNICITIES_FIELD, list("-")
                    )
                ).strip("[]"),
                str(
                    assignment.student["fields"].get("Product Opt Out Text", list("-"))
                ).strip("[]"),
                assignment.student["fields"].get(SURVEY_STUDENT_TIMEZONE_FIELD, "-"),
            )
        )

        # This actually writes the teams to the DAO
        # projectsdao.assign_student_to_project(
        #     assignment.student, assignment.project, assignment.score
        # )


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
            project_name = project["fields"][PROJECT_TABLE_NAME_FIELD]
            student_name = student["fields"][STUDENT_TABLE_NAME_FIELD][0]
            print("==================================================================")
            print("Start scoring {} - {}".format(project_name, student_name))

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

            print("\nDone scoring {} - {}".format(project_name, student_name))
            print("==================================================================")

    return best_assignment


def __get_score(project: dict, student: dict) -> int:
    score = 0

    # print(f"Project {project}")
    project_name = project["fields"][PROJECT_TABLE_NAME_FIELD]
    student_name = student["fields"][STUDENT_TABLE_NAME_FIELD][0]
    print("Scoring {} for project {}".format(student_name, project_name))

    # =======================================================================================
    # Match student track to project required track
    # =======================================================================================
    print("\n== Track Scoring ==")
    project_tracks = project["fields"][PROJECT_TABLE_PROGRAMS_FIELD]
    print("Project programs: {}".format(project_tracks))

    student_track = student["fields"][STUDENT_TABLE_TRACK_FIELD]
    print("Student Track: {}".format(student_track))

    if student_track.upper() not in project_tracks.upper():
        print(
            "Student {} track not needed in project {}".format(
                student_name, project_name
            )
        )
        return -10000

    # =======================================================================================
    # Check to see if the student has opted out of this product
    # =======================================================================================
    print("\n== Product Opt Out Scoring ==")
    student_opt_out_products = student["fields"].get(
        SURVEY_TABLE_PRODUCT_OPT_OUT_FIELD, None
    )
    if student_opt_out_products:
        print(
            f"Student {student_name} opted out of products: {student_opt_out_products}"
        )

        product_name = project["fields"][PROJECT_TABLE_PRODUCT_NAME_FIELD][0]
        if product_name.upper() in (x.upper() for x in student_opt_out_products):
            print(f"Will not place {student_name} on product {product_name}")
            return -10000

    # =========================================================================
    # Returns a score reflecting how far this student will push team size from
    # the average
    # =========================================================================
    print("\n== Team Size Scoring ==")
    team_size_score = __calculate_team_size_score(project, student)
    print("Adding team size score: {}".format(team_size_score))
    score += team_size_score

    # =======================================================================================
    # Returns a score reflecting how compatible the student is with other team members
    # =======================================================================================
    print("\n== Team Compatibility Scoring ==")
    team_compatibility_score = __calculate_student_to_team_compatibility_score(
        project, student
    )
    print("Adding team compatibility score: {}".format(team_compatibility_score))
    score += team_compatibility_score

    # =======================================================================================
    # These calculations prefer the creation of diverse teams
    # =======================================================================================
    print("\n== Ethnic Diversity Scoring ==")
    ethnic_diversity_score = __calculate_ethnic_diversity_score(project, student)
    print("Adding ethnic diversity score: {}".format(ethnic_diversity_score))
    score += ethnic_diversity_score

    print("\n== Gender Diversity Scoring ==")
    gender_diversity_score = __calculate_gender_diversity_score(project, student)
    print("Adding gender diversity score: {}".format(gender_diversity_score))
    score += gender_diversity_score

    # =======================================================================================
    # Align team members by timezone
    # =======================================================================================
    print("\n== {} ==".format(SURVEY_STUDENT_TIMEZONE_FIELD))
    timezone_score = __calculate_score_for_average_goal(
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
    print("\n== {} ==".format(SURVEY_TABLE_FRONTEND_FIELD))
    web_focus_score = __calculate_score_for_average_goal(
        project,
        student,
        SURVEY_TABLE_FRONTEND_FIELD,
        3.00,
        SURVEY_TABLE_FRONTEND_WEIGHT,
    )
    score += web_focus_score

    print("\n== {} ==".format(SURVEY_TABLE_DATA_MODELING_FIELD))
    web_data_modeling_score = __calculate_score_for_average_goal(
        project,
        student,
        SURVEY_TABLE_DATA_MODELING_FIELD,
        3.00,
        SURVEY_TABLE_DATA_MODELING_WEIGHT,
    )
    score += web_data_modeling_score

    print("\n== {} ==".format(SURVEY_TABLE_WEB_DESIGN_FIELD))
    web_design_score = __calculate_score_for_average_goal(
        project,
        student,
        SURVEY_TABLE_WEB_DESIGN_FIELD,
        3.00,
        SURVEY_TABLE_WEB_DESIGN_WEIGHT,
    )
    score += web_design_score

    print("\n== {} ==".format(SURVEY_TABLE_ASSERTIVENESS_FIELD))
    assertiveness_score = __calculate_score_for_average_goal(
        project, student, SURVEY_TABLE_ASSERTIVENESS_FIELD, 3.00, 5
    )
    score += assertiveness_score

    print("\n== {} ==".format(SURVEY_TABLE_PLANNING_FIELD))
    planning_score = __calculate_score_for_average_goal(
        project, student, SURVEY_TABLE_PLANNING_FIELD, 3.00, 5
    )
    score += planning_score

    VISION = "Are you more interested in the big picture or details?"
    print("\n== {} ==".format(VISION))
    vision_score = __calculate_score_for_average_goal(project, student, VISION, 3.00, 5)
    score += vision_score

    return score


def __calculate_team_size_score(project: dict, student: dict) -> int:
    project_name = project["fields"][PROJECT_TABLE_NAME_FIELD]
    student_track = student["fields"][STUDENT_TABLE_TRACK_FIELD]

    # Calculate the current average team size for this track
    average_team_size = __get_average_team_size_for_track(student_track)

    # Calculate the size of the current team
    team_member_count = __count_team_assignments(project, student_track)
    print(
        "Project ({}) has {} members in the {} track; average is {}".format(
            project_name, team_member_count, student_track, average_team_size
        )
    )

    score = math.ceil(SCORE_WEIGHT_TEAM_SIZE * (average_team_size - team_member_count))

    return score


def __get_average_team_size_for_track(track: str) -> float:
    assignments_for_track = []
    for assignment in assignments:
        if (
            assignment.student["fields"][STUDENT_TABLE_TRACK_FIELD].upper()
            == track.upper()
        ):
            assignments_for_track.append(assignment)

    number_of_assignments = len(assignments_for_track)

    teams_requiring_track = []
    for project in projects:
        if track.upper() in project["fields"][PROJECT_TABLE_PROGRAMS_FIELD].upper():
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
    project_name = project["fields"][PROJECT_TABLE_NAME_FIELD]
    student_name = student["fields"][STUDENT_TABLE_NAME_FIELD][0]

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
    if (
        team_response_average > desired_average
        and student_response < team_response_average
    ):
        # Yes, we want this student on the team. The team average is higher than
        # desired and they'll pull the average down.
        score = weight
    elif (
        team_response_average > desired_average
        and student_response > team_response_average
    ):
        # No, we don't want this student on the team. The team average is higher than
        # desired and they'll push the average up.
        score = -weight
    elif (
        team_response_average < desired_average
        and student_response > team_response_average
    ):
        # Yes, we want this student on the team. The team average is lower than desired
        # and they'll push the average up.
        score = weight
    elif (
        team_response_average < desired_average
        and student_response < team_response_average
    ):
        # No, we don't want this student on the team. The team average is lower than
        # desired and they'll pull the average down.
        score = -weight

    print(
        "Score: {} (Based on team average {} and student response {})".format(
            score, team_response_average, student_response
        )
    )

    # Note the score may be zero
    return score


def __calculate_student_to_team_compatibility_score(
    project: dict, student: dict
) -> int:
    project_name = project["fields"][PROJECT_TABLE_NAME_FIELD]
    student_name = student["fields"][STUDENT_TABLE_NAME_FIELD][0]

    print(
        "Calculating compatibility score for: Project({}) - Student({})".format(
            project_name, student_name
        )
    )

    # Check to see if the student responded to the survey, question
    # print(student['fields'])
    if STUDENT_TABLE_INCOMPATIBLE_STUDENT_NAMES_FIELD not in student["fields"]:
        # If not, this has no effect on the score
        return 0

    student_not_compatible_list = student["fields"][
        STUDENT_TABLE_INCOMPATIBLE_STUDENT_NAMES_FIELD
    ]
    print(
        "Checking incompatibility list for student {}: {}".format(
            student_name, student_not_compatible_list
        )
    )

    # Get the list of current assignments for the project team
    team_assignments = __get_team_assignments(project)

    for assignment in team_assignments:
        assigned_student_name = assignment.student["fields"][STUDENT_TABLE_NAME_FIELD][
            0
        ]

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
        if (
            STUDENT_TABLE_INCOMPATIBLE_STUDENT_NAMES_FIELD
            in assignment.student["fields"]
        ):
            for incompatibleStudent in assignment.student["fields"][
                STUDENT_TABLE_INCOMPATIBLE_STUDENT_NAMES_FIELD
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


def __calculate_ethnic_diversity_score(project: dict, student: dict) -> int:
    """Calculates a scrore that indicates if this student will complete a ethnic pair
    on the team. This will try to always have at least 2 people who share the same
    ethnic identity on the same team.

    Parameters:
        project -- The project
        student -- The student

    Returns:
        A score
    """
    project_name = project["fields"][PROJECT_TABLE_NAME_FIELD]
    student_name = student["fields"][STUDENT_TABLE_NAME_FIELD][0]

    print(
        "Calculating ethnic pairing score for: Project({}) - Student({})".format(
            project_name, student_name
        )
    )

    # Get the ethnicities specified by the student
    student_ethnicities = student["fields"].get(SURVEY_TABLE_ETHNICITIES_FIELD, None)
    if not student_ethnicities:
        # The student didn't specify ethnicities, so we can't calculate a score
        return 0

    # Get the list of current assignments for the project team
    team_assignments = __get_team_assignments(project)

    # This list will hold the list of ethnicities on the team
    team_ethnicities = []
    for assignment in team_assignments:
        assigned_student_ethnicities = assignment.student["fields"].get(
            SURVEY_TABLE_ETHNICITIES_FIELD, None
        )

        if assigned_student_ethnicities:
            team_ethnicities.append(assigned_student_ethnicities)

    # Team ethnicities is going to be a list of lists, so let's flatten it
    team_ethnicities = [item for sublist in team_ethnicities for item in sublist]

    # ================================================================================================================
    # Get the count ethnicities for the already assigned students
    ethnicity_counter = __get_ethnicity_counter()
    ethnicity_counter.update(team_ethnicities)

    # Check each of the student's listed ethnicities and take the highest score
    best_ethnicity_score = -100
    for student_ethnicity in student_ethnicities:
        matching_ethnicity_count = ethnicity_counter.get(student_ethnicity)

        current_ethnicity_score = -100

        if matching_ethnicity_count == 0:
            # This is good, as it will make the team more diverse
            current_ethnicity_score = 100
        if matching_ethnicity_count == 1:
            # This is better, as it will pair students with like ethnicities
            current_ethnicity_score = 200

        # Check to see if this is a better match
        if current_ethnicity_score > best_ethnicity_score:
            best_ethnicity_score = current_ethnicity_score

    return best_ethnicity_score


def __get_ethnicity_counter() -> Counter:
    ethnicity_counter = Counter(
        {
            "Asian (East Asian, Southeast Asian, South Asian)": 0,
            "Middle Eastern or North African": 0,
            "Black, African or African American": 0,
            "White or Caucasian": 0,
            "Native Hawaiian or Pacific Islander": 0,
            "Hispanic or LatinX": 0,
            "American Indian, Alaskan Native or Indigenous": 0,
        }
    )

    return ethnicity_counter


def __calculate_gender_diversity_score(project: dict, student: dict) -> int:
    """Calculates a scrore that indicates if this student will complete a gender pair
    on the team. This will try to always have at least 2 people who share the same
    gender identity on the same team.

    Parameters:
        project -- The project
        student -- The student

    Returns:
        A score
    """
    project_name = project["fields"][PROJECT_TABLE_NAME_FIELD]
    student_name = student["fields"][STUDENT_TABLE_NAME_FIELD][0]

    print(
        "Calculating gender pairing score for: Project({}) - Student({})".format(
            project_name, student_name
        )
    )

    # Get the gender specified by the student
    student_gender = student["fields"].get(SURVEY_TABLE_GENDER_FIELD, None)
    if not student_gender:
        # The student didn't provide a gender, so we can't calculate a score
        return 0

    # Get the list of current assignments for the project team
    team_assignments = __get_team_assignments(project)

    # This list will hold the list of genders on the team
    team_gender_values = []
    for assignment in team_assignments:
        assigned_student_gender = assignment.student["fields"].get(
            SURVEY_TABLE_GENDER_FIELD, None
        )

        if assigned_student_gender:
            team_gender_values.append(assigned_student_gender)

    # ================================================================================================================
    # Get the count genders for the already assigned students
    gender_counter = __get_gender_counter()
    gender_counter.update(team_gender_values)

    # Get the count of the particular gender that matches the student
    matching_gender_count = gender_counter.get(student_gender)

    if matching_gender_count == 0:
        # This is good, as it will make the team more diverse
        return 100
    if matching_gender_count == 1:
        # This is better, as it will pair students with like genders
        return 200
    else:
        # There are already at least 2 student with this gender identity, so we won't
        # prefer this
        return matching_gender_count * -100


def __get_gender_counter() -> Counter:
    gender_counter = Counter(
        {
            "Cisgender Man": 0,
            "Cisgender Woman": 0,
            "Transgender Man": 0,
            "Transgender Woman": 0,
            "Non-Binary": 0,
            "Gender-Queer / Gender-Fluid": 0,
        }
    )

    return gender_counter


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
                assignment.student["fields"][STUDENT_TABLE_TRACK_FIELD].upper()
                == track.upper()
            ):
                number_of_assignments += 1

    return number_of_assignments
