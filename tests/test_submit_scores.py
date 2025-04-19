from django.test import TestCase
from esports.models import League_Game, Match, League_Team, Match_Survey, Match_Date, League_Level, Player, School_Team, School_Team_Player
from esports.views.league_views import submit_scores

class SubmitScoresTests(TestCase):
    def setUp(self):
        # Create a league level (used to define if roster/scouting checks are required)
        self.league_level = League_Level.objects.create(level_of_play="Champion")

        # Create a league game associated with the level
        self.league_game = League_Game.objects.create(
            activate=True,
            series_length=3,         # Best-of-3
            show_bracket=True,       # Bracket enabled
            league_level=self.league_level
        )

        # Create a match date associated with the league game
        self.match_date = Match_Date.objects.create(
            league_game=self.league_game,
            match_date='2024-01-01'
        )

        # Create 2 School Teams
        self.school_team1 = School_Team.objects.create(team_name='School A')
        self.school_team2 = School_Team.objects.create(team_name='School B')

        # Create two teams that are part of the league and same bracket
        self.team1 = League_Team.objects.create(
            school_team=self.school_team1,
            league_game=self.league_game,
            bracket_number=1,
            seeding=2
        )
        self.team2 = League_Team.objects.create(
            school_team=self.school_team2,
            league_game=self.league_game,
            bracket_number=1,
            seeding=1
        )

        # Create a match between the two teams in the bracket
        self.match = Match.objects.create(
            home_team=self.team1,
            away_team=self.team2,
            match_date=self.match_date,
            tourney_match=True,
            tourney_number=1,
            bracket_number=1
        )

        # Create 2 Player objects to use as School Team Players
        self.player_a_base = Player.objects.create(player_name="Player A")
        self.player_b_base = Player.objects.create(player_name="Player B")


        # Create 2 School Team Players for POG inputs
        self.player_a = School_Team_Player.objects.create(
            school_team=self.school_team1,
            player=self.player_a_base
        )

        self.player_b = School_Team_Player.objects.create(
            school_team=self.school_team2,
            player=self.player_b_base
        )

        # Create a match survey report from the home team perspective
        self.home_report = Match_Survey.objects.create(
            match=self.match,
            team=self.team1,
            other_team=self.team2,
            team_score=2,
            other_score=1,
            team_forfeit=False,
            other_forfeit=False,
            team_othersportsmanship=5,
            team_otherontime=True,
            team_pog=self.player_a,
            other_pog=self.player_b,
            roster_correct="Yes",
            scouting_correct="Yes",
            team_roster="Roster A"
        )

        # Create a match survey report from the away team perspective
        self.away_report = Match_Survey.objects.create(
            match=self.match,
            team=self.team2,
            other_team=self.team1,
            team_score=1,
            other_score=2,
            team_forfeit=False,
            other_forfeit=False,
            team_othersportsmanship=4,
            team_otherontime=True,
            team_pog=self.player_b,
            other_pog=self.player_a,
            roster_correct="Yes",
            scouting_correct="Yes",
            team_roster="Roster B"
        )

    def test_submit_scores_updates_match_and_teams(self):
        # Run the logic that processes the submitted scores
        submit_scores(self.match, self.home_report, self.away_report)

        # Reload match and teams from the database to reflect updates
        self.match.refresh_from_db()
        self.team1.refresh_from_db()
        self.team2.refresh_from_db()

        # Assert the match was marked complete and the score was applied
        self.assertTrue(self.match.complete)
        self.assertEqual(self.match.home_score, 2)
        self.assertEqual(self.match.away_score, 1)

        # Assert win/loss and point calculations
        self.assertEqual(self.team1.wins, 1)
        self.assertEqual(self.team2.losses, 1)
        self.assertEqual(self.team1.points, 3)  # 3 points per win
        self.assertEqual(self.team2.points, 0)

        # Assert that match survey reports were deleted
        self.assertFalse(Match_Survey.objects.filter(pk=self.home_report.pk).exists())
        self.assertFalse(Match_Survey.objects.filter(pk=self.away_report.pk).exists())
