import unittest

import teambuilding.handler


class TestGetScore(unittest.TestCase):
    def test_get_score_team_size(self):
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
        project_02 = {"fields": {"id": "project_02", teambuilding.handler.PROJECT_TRACKS_FIELD: ["WEB"]}}
        project_03 = {"fields": {"id": "project_03", teambuilding.handler.PROJECT_TRACKS_FIELD: ["DS"]}}
        projects = [project_01, project_02, project_03]

        # ==============================================================================
        # Setup the assignments
        # ==============================================================================
        assigned_student_01 = {
            "fields": {
                teambuilding.handler.SURVEY_TRACK_FIELD: "DS",
                teambuilding.handler.SURVEY_STUDENT_NAME_FIELD: ["Assigned Student 01"],
                teambuilding.handler.SURVEY_INCOMPATIBLE_STUDENT_NAMES_FIELD: ["Another Student"],
            }
        }

        assignments = [teambuilding.handler.AssignmentTuple(project_03, assigned_student_01, 100)]

        # ==============================================================================
        # Setup the unassigned student to score
        # ==============================================================================
        student_to_score = {
            "fields": {
                teambuilding.handler.SURVEY_TRACK_FIELD: "DS",
                teambuilding.handler.SURVEY_STUDENT_NAME_FIELD: ["Unassigned Student 01"],
                teambuilding.handler.SURVEY_INCOMPATIBLE_STUDENT_NAMES_FIELD: ["Another Student"],
            }
        }

        # ==============================================================================
        # Calculate the scores
        # ==============================================================================
        project_01_score = teambuilding.handler._get_score(projects, assignments, project_01, student_to_score)
        project_02_score = teambuilding.handler._get_score(projects, assignments, project_02, student_to_score)
        project_03_score = teambuilding.handler._get_score(projects, assignments, project_03, student_to_score)

        self.assertGreater(project_01_score, project_03_score)
        self.assertEquals(project_02_score, teambuilding.handler.BAD_FIT_SCORE)
        self.assertLess(project_03_score, project_01_score)

    def test_get_score_ethnic_diversity(self):
        """
        Scenario:
            Assign a DS student with ethnicity A to one of three DS projects
            Project 1: One DS student with ethnicity A (This is where we want the incoming student to go)
            Project 2: Two DS students with ethnicity A (Not here as there's already a pairing)
            Project 3: No DS students with ethnicity A (Not here, we don't want to leave the student in project 1 alone)

            Project 1 should score highest
            Project 2 should score lowest
            Project 3 in between
        """
        # ==============================================================================
        # Setup the projects
        # ==============================================================================
        project_01 = {"fields": {"id": "project_01", teambuilding.handler.PROJECT_TRACKS_FIELD: ["DS"]}}
        project_02 = {"fields": {"id": "project_02", teambuilding.handler.PROJECT_TRACKS_FIELD: ["DS"]}}
        project_03 = {"fields": {"id": "project_03", teambuilding.handler.PROJECT_TRACKS_FIELD: ["DS"]}}
        projects = [project_01, project_02, project_03]

        # ==============================================================================
        # Setup the assignments
        # ==============================================================================
        assigned_student_01 = {
            "fields": {
                teambuilding.handler.SURVEY_TRACK_FIELD: "DS",
                teambuilding.handler.SURVEY_STUDENT_NAME_FIELD: ["Assigned Student 01"],
                teambuilding.handler.SURVEY_ETHNICITIES_FIELD: ["ETHNICITY-A"],
            }
        }
        assigned_student_02 = {
            "fields": {
                teambuilding.handler.SURVEY_TRACK_FIELD: "DS",
                teambuilding.handler.SURVEY_STUDENT_NAME_FIELD: ["Assigned Student 02"],
                teambuilding.handler.SURVEY_ETHNICITIES_FIELD: ["ETHNICITY-A"],
            }
        }
        assigned_student_03 = {
            "fields": {
                teambuilding.handler.SURVEY_TRACK_FIELD: "DS",
                teambuilding.handler.SURVEY_STUDENT_NAME_FIELD: ["Assigned Student 03"],
                teambuilding.handler.SURVEY_ETHNICITIES_FIELD: ["ETHNICITY-A"],
            }
        }
        assigned_student_04 = {
            "fields": {
                teambuilding.handler.SURVEY_TRACK_FIELD: "DS",
                teambuilding.handler.SURVEY_STUDENT_NAME_FIELD: ["Assigned Student 04"],
                teambuilding.handler.SURVEY_ETHNICITIES_FIELD: ["ETHNICITY-B"],
            }
        }

        assignments = [
            teambuilding.handler.AssignmentTuple(project_01, assigned_student_01, 100),
            teambuilding.handler.AssignmentTuple(project_02, assigned_student_02, 100),
            teambuilding.handler.AssignmentTuple(project_02, assigned_student_03, 100),
            teambuilding.handler.AssignmentTuple(project_03, assigned_student_04, 100),
        ]

        # ==============================================================================
        # Setup the unassigned student to score
        # ==============================================================================
        student_to_score = {
            "fields": {
                teambuilding.handler.SURVEY_TRACK_FIELD: "DS",
                teambuilding.handler.SURVEY_STUDENT_NAME_FIELD: ["Unassigned Student 01"],
                teambuilding.handler.SURVEY_INCOMPATIBLE_STUDENT_NAMES_FIELD: ["Another Student"],
                teambuilding.handler.SURVEY_ETHNICITIES_FIELD: ["ETHNICITY-A"],
            }
        }

        # ==============================================================================
        # Calculate the scores
        # ==============================================================================
        project_01_score = teambuilding.handler._get_score(projects, assignments, project_01, student_to_score)
        project_02_score = teambuilding.handler._get_score(projects, assignments, project_02, student_to_score)
        project_03_score = teambuilding.handler._get_score(projects, assignments, project_03, student_to_score)

        # Project 1 score should be highest
        self.assertGreater(project_01_score, project_02_score)
        self.assertGreater(project_01_score, project_03_score)

        # Project 2 score should be lowest
        self.assertLess(project_02_score, project_01_score)
        self.assertLess(project_02_score, project_03_score)

        # Project 3 score should be in the middle
        self.assertLess(project_03_score, project_01_score)
        self.assertGreater(project_03_score, project_02_score)

    def test_get_score_gender_diversity(self):
        """
        Scenario:
            Assign a DS student with ethnicity A to one of three DS projects
            Project 1: One DS student with ethnicity A (This is where we want the incoming student to go)
            Project 2: Two DS students with ethnicity A (Not here as there's already a pairing)
            Project 3: No DS students with ethnicity A (Not here, we don't want to leave the student in project 1 alone)

            Project 1 should score highest
            Project 2 should score lowest
            Project 3 in between
        """
        # ==============================================================================
        # Setup the projects
        # ==============================================================================
        project_01 = {
            "id": "project_01",
            "fields": {"id": "project_01", teambuilding.handler.PROJECT_TRACKS_FIELD: ["DS"]},
        }
        project_02 = {
            "id": "project_02",
            "fields": {"id": "project_02", teambuilding.handler.PROJECT_TRACKS_FIELD: ["DS"]},
        }
        project_03 = {
            "id": "project_03",
            "fields": {"id": "project_03", teambuilding.handler.PROJECT_TRACKS_FIELD: ["DS"]},
        }
        projects = [project_01, project_02, project_03]

        # ==============================================================================
        # Setup the assignments
        # ==============================================================================
        assigned_student_01 = {
            "id": "assigned_student_01",
            "fields": {
                teambuilding.handler.SURVEY_TRACK_FIELD: "DS",
                teambuilding.handler.SURVEY_STUDENT_NAME_FIELD: ["Assigned Student 01"],
                teambuilding.handler.SURVEY_GENDER_FIELD: "GENDER-A",
            },
        }
        assigned_student_02 = {
            "id": "assigned_student_02",
            "fields": {
                teambuilding.handler.SURVEY_TRACK_FIELD: "DS",
                teambuilding.handler.SURVEY_STUDENT_NAME_FIELD: ["Assigned Student 02"],
                teambuilding.handler.SURVEY_GENDER_FIELD: "GENDER-A",
            },
        }
        assigned_student_03 = {
            "id": "assigned_student_03",
            "fields": {
                teambuilding.handler.SURVEY_TRACK_FIELD: "DS",
                teambuilding.handler.SURVEY_STUDENT_NAME_FIELD: ["Assigned Student 03"],
                teambuilding.handler.SURVEY_GENDER_FIELD: "GENDER-A",
            },
        }
        assigned_student_04 = {
            "id": "assigned_student_04",
            "fields": {
                teambuilding.handler.SURVEY_TRACK_FIELD: "DS",
                teambuilding.handler.SURVEY_STUDENT_NAME_FIELD: ["Assigned Student 04"],
                teambuilding.handler.SURVEY_GENDER_FIELD: "GENDER-B",
            },
        }

        assignments = [
            teambuilding.handler.AssignmentTuple(project_01, assigned_student_01, 100),
            teambuilding.handler.AssignmentTuple(project_02, assigned_student_02, 100),
            teambuilding.handler.AssignmentTuple(project_02, assigned_student_03, 100),
            teambuilding.handler.AssignmentTuple(project_03, assigned_student_04, 100),
        ]

        # ==============================================================================
        # Setup the unassigned student to score
        # ==============================================================================
        unassigned_student_01 = {
            "id": "unassigned_student_01",
            "fields": {
                teambuilding.handler.SURVEY_TRACK_FIELD: "DS",
                teambuilding.handler.SURVEY_STUDENT_NAME_FIELD: ["Unassigned Student 01"],
                teambuilding.handler.SURVEY_INCOMPATIBLE_STUDENT_NAMES_FIELD: ["Another Student"],
                teambuilding.handler.SURVEY_GENDER_FIELD: "GENDER-A",
            },
        }
        unassigned_students = [unassigned_student_01]

        # ==============================================================================
        # Calculate the scores
        # ==============================================================================
        project_01_score = teambuilding.handler._get_score(projects, assignments, project_01, unassigned_student_01)
        project_02_score = teambuilding.handler._get_score(projects, assignments, project_02, unassigned_student_01)
        project_03_score = teambuilding.handler._get_score(projects, assignments, project_03, unassigned_student_01)

        # Project 1 score should be highest
        self.assertGreater(project_01_score, project_02_score)
        self.assertGreater(project_01_score, project_03_score)

        # Project 2 score should be lowest
        self.assertLess(project_02_score, project_01_score)
        self.assertLess(project_02_score, project_03_score)

        # Project 3 score should be in the middle
        self.assertLess(project_03_score, project_01_score)
        self.assertGreater(project_03_score, project_02_score)

        best_assignment = teambuilding.handler._get_best_assignment(projects, assignments, unassigned_students)
        self.assertEquals(best_assignment.score, project_01_score)
