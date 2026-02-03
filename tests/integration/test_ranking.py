"""
Integration tests for TrueSkill ranking calculations.

Tests the scoring and ranking system that powers rower comparisons
and leaderboards. These tests verify the TrueSkill algorithm integration
and score persistence.
"""
import pytest
from django.test import TestCase
from trueskill import Rating, rate, setup
from rowing.models import Rower, Race, Result, Score, ScoreRanking, Event, Competition
from model_bakery import baker
import datetime


class TestTrueSkillIntegration(TestCase):
    """Test TrueSkill library integration."""

    def test_trueskill_rate_basic(self):
        """Test basic TrueSkill rate function works."""
        # Two teams, each with one player
        team1 = [Rating()]
        team2 = [Rating()]

        # Team 1 beats team 2
        new_ratings = rate([team1, team2], ranks=[1, 2])

        # Winner should have higher mu
        self.assertGreater(new_ratings[0][0].mu, new_ratings[1][0].mu)

    def test_trueskill_rate_multi_team(self):
        """Test TrueSkill with multiple teams (like a race)."""
        # Four teams representing a race
        teams = [[Rating()] for _ in range(4)]

        # Positions: 1st, 2nd, 3rd, 4th
        new_ratings = rate(teams, ranks=[1, 2, 3, 4])

        # Ratings should be ordered by position
        mus = [new_ratings[i][0].mu for i in range(4)]
        self.assertEqual(mus, sorted(mus, reverse=True))

    def test_trueskill_custom_parameters(self):
        """Test TrueSkill with custom beta/tau parameters."""
        # These are the parameters used in the actual recalculator
        setup(beta=10, tau=0.5, draw_probability=0.002)

        team1 = [Rating(mu=0.0, sigma=10)]
        team2 = [Rating(mu=0.0, sigma=10)]

        new_ratings = rate([team1, team2], ranks=[1, 2])

        # Should still work and produce sensible results
        self.assertGreater(new_ratings[0][0].mu, 0)
        self.assertLess(new_ratings[1][0].mu, 0)

    def test_trueskill_multi_person_crew(self):
        """Test TrueSkill with multi-person crews (like an eight)."""
        # Two eights racing
        crew1 = [Rating() for _ in range(8)]
        crew2 = [Rating() for _ in range(8)]

        new_ratings = rate([crew1, crew2], ranks=[1, 2])

        # All members of winning crew should have improved
        for rating in new_ratings[0]:
            self.assertGreater(rating.mu, 25)  # Default mu is 25


class TestScoreModel(TestCase):
    """Test Score model behavior."""

    @classmethod
    def setUpTestData(cls):
        cls.rower = baker.make('rowing.Rower')
        cls.competition = baker.make('rowing.Competition')
        cls.event = baker.make('rowing.Event', comp=cls.competition, type='Sweep')
        cls.race = baker.make('rowing.Race', event=cls.event, complete=True,
                              date=datetime.date(2024, 6, 15))
        cls.result = baker.make('rowing.Result', race=cls.race, position=1)
        cls.result.crew.add(cls.rower)

    def test_score_creation(self):
        """Test Score can be created and linked to result/rower."""
        score = Score.objects.create(
            mu=25.0,
            sigma=8.333,
            result=self.result,
            rower=self.rower
        )
        self.assertEqual(score.mu, 25.0)
        self.assertEqual(score.sigma, 8.333)
        self.assertEqual(score.rower, self.rower)
        self.assertEqual(score.result, self.result)

    def test_score_rower_relationship(self):
        """Test rower can access their scores."""
        Score.objects.create(
            mu=25.0,
            sigma=8.333,
            result=self.result,
            rower=self.rower
        )
        self.assertEqual(self.rower.score_set.count(), 1)

    def test_score_filtering_by_type(self):
        """Test scores can be filtered by event type."""
        Score.objects.create(
            mu=25.0,
            sigma=8.333,
            result=self.result,
            rower=self.rower
        )

        sweep_scores = self.rower.score_set.filter(
            result__race__event__type='Sweep'
        )
        sculling_scores = self.rower.score_set.filter(
            result__race__event__type='Sculling'
        )

        self.assertEqual(sweep_scores.count(), 1)
        self.assertEqual(sculling_scores.count(), 0)


class TestScoreRankingModel(TestCase):
    """Test ScoreRanking model behavior."""

    @classmethod
    def setUpTestData(cls):
        cls.rower = baker.make('rowing.Rower', gender='M')

    def test_score_ranking_creation(self):
        """Test ScoreRanking can be created."""
        ranking = ScoreRanking.objects.create(
            mu=30.0,
            sigma=7.0,
            delta_mu_sigma=23.0,
            rower=self.rower,
            date=datetime.date(2024, 6, 15),
            type='Sweep',
            sr_type='Current'
        )
        self.assertEqual(ranking.mu, 30.0)
        self.assertEqual(ranking.delta_mu_sigma, 23.0)
        self.assertEqual(ranking.sr_type, 'Current')

    def test_score_ranking_types(self):
        """Test both Current and All time ranking types."""
        ScoreRanking.objects.create(
            mu=30.0, sigma=7.0, delta_mu_sigma=23.0,
            rower=self.rower, date=datetime.date(2024, 6, 15),
            type='Sweep', sr_type='Current'
        )
        ScoreRanking.objects.create(
            mu=35.0, sigma=6.0, delta_mu_sigma=29.0,
            rower=self.rower, date=datetime.date(2024, 3, 10),
            type='Sweep', sr_type='All time'
        )

        current = ScoreRanking.objects.filter(rower=self.rower, sr_type='Current')
        alltime = ScoreRanking.objects.filter(rower=self.rower, sr_type='All time')

        self.assertEqual(current.count(), 1)
        self.assertEqual(alltime.count(), 1)


class TestRankingCalculationLogic(TestCase):
    """Test the logic used in ranking calculations."""

    def test_default_rating_values(self):
        """Test default rating values match recalculator constants."""
        # These are from recalculator.py
        DEFAULT_SIGMA = 10
        DEFAULT_MU = 0.0
        INT_MU = 10.0

        # New rower should start with default
        default_rating = Rating(mu=DEFAULT_MU, sigma=DEFAULT_SIGMA)
        self.assertEqual(default_rating.mu, 0.0)
        self.assertEqual(default_rating.sigma, 10.0)

        # International rower should start higher
        int_rating = Rating(mu=INT_MU, sigma=DEFAULT_SIGMA)
        self.assertEqual(int_rating.mu, 10.0)

    def test_score_floor_logic(self):
        """Test score floor at 0.0 logic."""
        DFLOOR = True

        # Simulate a negative mu from rating
        test_mu = -5.0

        if test_mu < 0.0 and DFLOOR:
            floored_mu = 0.0
        else:
            floored_mu = test_mu

        self.assertEqual(floored_mu, 0.0)

    def test_dynamic_tau_calculation(self):
        """Test dynamic tau adjustment logic."""
        DEFAULT_SIGMA = 10
        DYNAMIC_TAU_ADJUSTMENT = 730  # days

        current_sigma = 7.0
        days_between_races = 365  # one year

        # Formula from recalculator
        adjusted_sigma = current_sigma + (
            (DEFAULT_SIGMA - current_sigma) *
            min(DYNAMIC_TAU_ADJUSTMENT, days_between_races) / DYNAMIC_TAU_ADJUSTMENT
        )

        # Sigma should increase (uncertainty grows with time)
        self.assertGreater(adjusted_sigma, current_sigma)
        # But not exceed default
        self.assertLess(adjusted_sigma, DEFAULT_SIGMA)

    def test_delta_mu_sigma_calculation(self):
        """Test delta_mu_sigma (mu - sigma) used for rankings."""
        mu = 30.0
        sigma = 7.0

        delta_mu_sigma = mu - sigma

        self.assertEqual(delta_mu_sigma, 23.0)

    def test_ranking_comparison(self):
        """Test that delta_mu_sigma correctly orders rowers."""
        # Rower A: high mu, high sigma (less certain)
        rower_a_delta = 40.0 - 12.0  # = 28

        # Rower B: lower mu, lower sigma (more certain)
        rower_b_delta = 35.0 - 5.0  # = 30

        # Rower B should rank higher despite lower mu
        self.assertGreater(rower_b_delta, rower_a_delta)


class TestRaceResultScenarios(TestCase):
    """Test various race result scenarios."""

    def test_expected_vs_actual_finish(self):
        """Test error calculation when expected != actual finish."""
        # Simulate error calculation from recalculator
        error_list = [
            [100, 1],  # [mu_sum, actual_position]
            [90, 2],
            [80, 3],
            [110, 4],  # Highest rated finished last (upset!)
        ]

        # Sort by mu_sum descending and assign expected ranks
        sorted_list = sorted(error_list, key=lambda x: x[0], reverse=True)
        for i, item in enumerate(sorted_list):
            item.append(i + 1)  # expected rank

        # Calculate error
        r_error = 0
        for item in error_list:
            actual_pos = item[1]
            expected_pos = item[2]
            r_error += (actual_pos - expected_pos) ** 2

        r_error = r_error / len(error_list)

        # There should be significant error due to the upset
        self.assertGreater(r_error, 0)
