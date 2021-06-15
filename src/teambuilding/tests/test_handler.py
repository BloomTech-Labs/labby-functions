import unittest

import teambuilding.handler


class TestCalculateStudentToTeamCompatibilityScore(unittest.TestCase):
    def test_no_assignments(self):
        """
        No assignments have been made
        """
        assignments = []
        project = {"fields": {}}
        student = {"fields": {teambuilding.handler.SURVEY_STUDENT_NAME_FIELD: ["Test Student 01"]}}

        score = teambuilding.handler._calculate_student_to_team_compatibility_score(assignments, project, student)

        self.assertEqual(score, 0)

    def test_no_incompatibilities(self):
        """
        No incompatibilities have been listed
        """
        assigned_student_01 = {
            "fields": {
                teambuilding.handler.SURVEY_STUDENT_NAME_FIELD: ["Assigned Student 01"],
                teambuilding.handler.SURVEY_INCOMPATIBLE_STUDENT_NAMES_FIELD: ["Another Student"],
            }
        }
        project_01 = {"fields": {"id": "project_01"}}

        assignments = [teambuilding.handler.AssignmentTuple(project_01, assigned_student_01, 100)]

        student_being_scored = {"fields": {teambuilding.handler.SURVEY_STUDENT_NAME_FIELD: ["Test Student 01"]}}

        score = teambuilding.handler._calculate_student_to_team_compatibility_score(
            assignments, project_01, student_being_scored
        )

        self.assertEqual(score, 0)

    def test_not_incompatible(self):
        """
        Both students list incompatibilites, but not with each other
        """
        assigned_student_01 = {
            "fields": {
                teambuilding.handler.SURVEY_STUDENT_NAME_FIELD: ["Assigned Student 01"],
                teambuilding.handler.SURVEY_INCOMPATIBLE_STUDENT_NAMES_FIELD: ["Yet Another Student"],
            }
        }
        project_01 = {"fields": {"id": "project_01"}}

        assignments = [teambuilding.handler.AssignmentTuple(project_01, assigned_student_01, 100)]

        student_being_scored = {
            "fields": {
                teambuilding.handler.SURVEY_STUDENT_NAME_FIELD: ["Test Student 01"],
                teambuilding.handler.SURVEY_INCOMPATIBLE_STUDENT_NAMES_FIELD: ["Yet Another Student"],
            }
        }

        score = teambuilding.handler._calculate_student_to_team_compatibility_score(
            assignments, project_01, student_being_scored
        )

        self.assertEqual(score, 0)

    def test_unassigned_student_incompatible(self):
        """
        Student being scored lists an already assigned student as incompatible
        """
        assigned_student_01 = {
            "fields": {
                teambuilding.handler.SURVEY_STUDENT_NAME_FIELD: ["Assigned Student 01"],
                teambuilding.handler.SURVEY_INCOMPATIBLE_STUDENT_NAMES_FIELD: [],
            }
        }
        project_01 = {"fields": {"id": "project_01"}}

        assignments = [teambuilding.handler.AssignmentTuple(project_01, assigned_student_01, 100)]

        student_being_scored = {
            "fields": {
                teambuilding.handler.SURVEY_STUDENT_NAME_FIELD: ["Test Student 01"],
                teambuilding.handler.SURVEY_INCOMPATIBLE_STUDENT_NAMES_FIELD: ["Assigned Student 01"],
            }
        }

        score = teambuilding.handler._calculate_student_to_team_compatibility_score(
            assignments, project_01, student_being_scored
        )

        self.assertEqual(score, -100000)

    def test_assigned_student_incompatible(self):
        """
        Student being scored is listed as incompatible by an already assigned student
        """
        assigned_student_01 = {
            "fields": {
                teambuilding.handler.SURVEY_STUDENT_NAME_FIELD: ["Assigned Student 01"],
                teambuilding.handler.SURVEY_INCOMPATIBLE_STUDENT_NAMES_FIELD: ["Test Student 01"],
            }
        }
        project_01 = {"fields": {"id": "project_01"}}

        assignments = [teambuilding.handler.AssignmentTuple(project_01, assigned_student_01, 100)]

        student_being_scored = {
            "fields": {
                teambuilding.handler.SURVEY_STUDENT_NAME_FIELD: ["Test Student 01"],
                teambuilding.handler.SURVEY_INCOMPATIBLE_STUDENT_NAMES_FIELD: [],
            }
        }

        score = teambuilding.handler._calculate_student_to_team_compatibility_score(
            assignments, project_01, student_being_scored
        )

        self.assertEqual(score, -100000)

    def test_average_teams_size_for_track_simple(self):
        """
        One assignment and one project, should be 1 average
        """
        project_01 = {"fields": {"id": "project_01", teambuilding.handler.PROJECT_TRACKS_FIELD: ["DS"]}}
        projects = [project_01]

        assigned_student_01 = {
            "fields": {
                teambuilding.handler.SURVEY_TRACK_FIELD: "DS",
            }
        }

        assignments = [teambuilding.handler.AssignmentTuple(project_01, assigned_student_01, 100)]

        score = teambuilding.handler._get_average_team_size_for_track(projects, assignments, "DS")

        self.assertEqual(score, 1.0)

    def test_average_teams_size_for_track_half(self):
        """
        One assignment and two projects, should be .5 average
        """
        project_01 = {"fields": {"id": "project_01", teambuilding.handler.PROJECT_TRACKS_FIELD: ["DS"]}}
        project_02 = {"fields": {"id": "project_02", teambuilding.handler.PROJECT_TRACKS_FIELD: ["DS"]}}
        projects = [project_01, project_02]

        assigned_student_01 = {
            "fields": {
                teambuilding.handler.SURVEY_TRACK_FIELD: "DS",
            }
        }

        assignment_01 = teambuilding.handler.AssignmentTuple(project_01, assigned_student_01, 100)
        assignments = [assignment_01]

        score = teambuilding.handler._get_average_team_size_for_track(projects, assignments, "DS")

        self.assertEqual(score, 0.5)

    def test_average_teams_size_for_track_half_with_extra(self):
        """
        Throw in some extra projects and assignments
        """
        project_01 = {"fields": {"id": "project_01", teambuilding.handler.PROJECT_TRACKS_FIELD: ["DS"]}}
        project_02 = {"fields": {"id": "project_02", teambuilding.handler.PROJECT_TRACKS_FIELD: ["NOTDS"]}}
        project_03 = {"fields": {"id": "project_02", teambuilding.handler.PROJECT_TRACKS_FIELD: ["DS"]}}
        project_04 = {"fields": {"id": "project_02", teambuilding.handler.PROJECT_TRACKS_FIELD: ["SOMETHINGELSE"]}}
        projects = [project_01, project_02, project_03, project_04]

        student_01 = {
            "fields": {
                teambuilding.handler.SURVEY_TRACK_FIELD: "DS",
            }
        }
        student_02 = {
            "fields": {
                teambuilding.handler.SURVEY_TRACK_FIELD: "NOTDS",
            }
        }

        assignment_01 = teambuilding.handler.AssignmentTuple(project_01, student_01, 100)
        assignment_02 = teambuilding.handler.AssignmentTuple(project_03, student_02, 100)
        assignments = [assignment_01, assignment_02]

        ds_score = teambuilding.handler._get_average_team_size_for_track(projects, assignments, "DS")

        self.assertEqual(ds_score, 0.5)

        not_ds_score = teambuilding.handler._get_average_team_size_for_track(projects, assignments, "NOTDS")

        self.assertEqual(not_ds_score, 1)

        something_else_score = teambuilding.handler._get_average_team_size_for_track(
            projects, assignments, "SOMETHINGELSE"
        )

        self.assertEqual(something_else_score, 0)

    def test_calculate_team_size_score_basic(self):
        """
        Scenario:
            Two DS projects
            Project 1 already has a DS student assigned
            Project 2 has no DS students assigned

            Project 2 score should be higher than Project 1 score to keep team sizes consistent
        """
        # ==============================================================================
        # Setup the projects
        # ==============================================================================
        project_01 = {"fields": {"id": "project_01", teambuilding.handler.PROJECT_TRACKS_FIELD: ["DS"]}}
        project_02 = {"fields": {"id": "project_02", teambuilding.handler.PROJECT_TRACKS_FIELD: ["DS"]}}
        projects = [project_01, project_02]

        # ==============================================================================
        # Setup the assignments
        # ==============================================================================
        assigned_student_01 = {
            "fields": {
                teambuilding.handler.SURVEY_TRACK_FIELD: "DS",
            }
        }

        assignment_01 = teambuilding.handler.AssignmentTuple(project_01, assigned_student_01, 100)
        assignments = [assignment_01]

        # ==============================================================================
        # Setup the unassigned student to score
        # ==============================================================================
        student_to_score = {
            "fields": {
                teambuilding.handler.SURVEY_TRACK_FIELD: "DS",
            }
        }

        # ==============================================================================
        # Calculate the scores
        # ==============================================================================
        project_01_score = teambuilding.handler._calculate_team_size_score(
            projects, assignments, project_01, student_to_score
        )
        project_02_score = teambuilding.handler._calculate_team_size_score(
            projects, assignments, project_02, student_to_score
        )

        self.assertGreater(project_02_score, project_01_score)

    def test_calculate_team_size_score_equal(self):
        """
        Scenario:
            Two DS projects
            Neither has a DS student assigned

            Scores for both projects should be zero since there's no affect
        """
        # ==============================================================================
        # Setup the projects
        # ==============================================================================
        project_01 = {"fields": {"id": "project_01", teambuilding.handler.PROJECT_TRACKS_FIELD: ["DS"]}}
        project_02 = {"fields": {"id": "project_02", teambuilding.handler.PROJECT_TRACKS_FIELD: ["DS"]}}
        projects = [project_01, project_02]

        # ==============================================================================
        # Setup the assignments
        # ==============================================================================
        assignments = []

        # ==============================================================================
        # Setup the unassigned student to score
        # ==============================================================================
        student_to_score = {
            "fields": {
                teambuilding.handler.SURVEY_TRACK_FIELD: "DS",
            }
        }

        # ==============================================================================
        # Calculate the scores
        # ==============================================================================
        project_01_score = teambuilding.handler._calculate_team_size_score(
            projects, assignments, project_01, student_to_score
        )
        project_02_score = teambuilding.handler._calculate_team_size_score(
            projects, assignments, project_02, student_to_score
        )

        self.assertEquals(project_01_score, 0)
        self.assertEquals(project_01_score, 0)
