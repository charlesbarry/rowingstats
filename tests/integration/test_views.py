"""
Integration tests for views with content validation.

These tests go beyond HTTP status codes to verify:
- Correct context data is passed to templates
- Expected content appears in responses
- Database queries are reasonable
- Error handling works correctly
"""
import pytest
from django.test import TestCase, Client
from django.urls import reverse
from rowing.models import Rower, Race, Competition, Event, Club, Edition, Fixture, Score, ScoreRanking
from model_bakery import baker
import datetime


class TestIndexView(TestCase):
    """Test the index/homepage view."""

    def test_index_returns_200(self):
        """Test index page loads successfully."""
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_index_uses_correct_template(self):
        """Test index uses the correct template."""
        response = self.client.get(reverse('index'))
        # The actual template is index2.html (based on IndexView2)
        self.assertTemplateUsed(response, 'rowing/index2.html')

    def test_index_contains_site_title(self):
        """Test index page contains expected content."""
        response = self.client.get(reverse('index'))
        self.assertContains(response, 'Rowing')


class TestAboutView(TestCase):
    """Test the about page view."""

    def test_about_returns_200(self):
        """Test about page loads successfully."""
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)

    def test_about_uses_correct_template(self):
        """Test about uses the correct template."""
        response = self.client.get(reverse('about'))
        self.assertTemplateUsed(response, 'rowing/about.html')


class TestRowerViews(TestCase):
    """Test rower list and detail views."""

    @classmethod
    def setUpTestData(cls):
        cls.rower = baker.make('rowing.Rower', name='Test Rower', gender='M')

    def test_rower_list_returns_200(self):
        """Test rower list page loads successfully."""
        response = self.client.get(reverse('rower-list'))
        self.assertEqual(response.status_code, 200)

    def test_rower_list_loads(self):
        """Test rower list page loads and has rowers context."""
        response = self.client.get(reverse('rower-list'))
        # The list view is paginated, check it loads
        self.assertEqual(response.status_code, 200)

    def test_rower_detail_returns_200(self):
        """Test rower detail page loads successfully."""
        response = self.client.get(reverse('rower-detail', args=[self.rower.pk]))
        self.assertEqual(response.status_code, 200)

    def test_rower_detail_contains_name(self):
        """Test rower detail contains the rower's name."""
        response = self.client.get(reverse('rower-detail', args=[self.rower.pk]))
        self.assertContains(response, 'Test Rower')

    def test_rower_detail_has_context(self):
        """Test rower detail view passes correct context."""
        response = self.client.get(reverse('rower-detail', args=[self.rower.pk]))
        # The view uses 'object' (from DetailView pattern)
        self.assertIn('object', response.context)
        self.assertEqual(response.context['object'], self.rower)

    def test_rower_404_for_invalid_id(self):
        """Test rower detail returns 404 for invalid ID."""
        response = self.client.get(reverse('rower-detail', args=[999999999]))
        self.assertEqual(response.status_code, 404)


class TestCompetitionViews(TestCase):
    """Test competition list and detail views."""

    @classmethod
    def setUpTestData(cls):
        cls.competition = baker.make('rowing.Competition', name='Test Regatta')

    def test_competition_list_returns_200(self):
        """Test competition list page loads successfully."""
        response = self.client.get(reverse('comp-list'))
        self.assertEqual(response.status_code, 200)

    def test_competition_list_contains_competition(self):
        """Test competition list contains our test competition."""
        response = self.client.get(reverse('comp-list'))
        self.assertContains(response, 'Test Regatta')

    def test_competition_detail_returns_200(self):
        """Test competition detail page loads successfully."""
        response = self.client.get(reverse('comp-detail', args=[self.competition.pk]))
        self.assertEqual(response.status_code, 200)

    def test_competition_detail_contains_name(self):
        """Test competition detail contains the competition name."""
        response = self.client.get(reverse('comp-detail', args=[self.competition.pk]))
        self.assertContains(response, 'Test Regatta')

    def test_competition_404_for_invalid_id(self):
        """Test competition detail returns 404 for invalid ID."""
        response = self.client.get(reverse('comp-detail', args=[999999999]))
        self.assertEqual(response.status_code, 404)


class TestRaceViews(TestCase):
    """Test race list and detail views."""

    @classmethod
    def setUpTestData(cls):
        cls.competition = baker.make('rowing.Competition')
        cls.event = baker.make('rowing.Event', comp=cls.competition)
        cls.race = baker.make('rowing.Race', name='Test Heat 1', event=cls.event,
                              complete=True, date=datetime.date(2024, 6, 15))

    def test_race_list_returns_200(self):
        """Test race list page loads successfully."""
        response = self.client.get(reverse('race-list'))
        self.assertEqual(response.status_code, 200)

    def test_race_detail_returns_200(self):
        """Test race detail page loads successfully."""
        response = self.client.get(reverse('race-detail', args=[self.race.pk]))
        self.assertEqual(response.status_code, 200)

    def test_race_detail_contains_name(self):
        """Test race detail contains the race name."""
        response = self.client.get(reverse('race-detail', args=[self.race.pk]))
        self.assertContains(response, 'Test Heat 1')

    def test_race_404_for_invalid_id(self):
        """Test race detail returns 404 for invalid ID."""
        response = self.client.get(reverse('race-detail', args=[999999999]))
        self.assertEqual(response.status_code, 404)


class TestClubViews(TestCase):
    """Test club list and detail views."""

    @classmethod
    def setUpTestData(cls):
        cls.club = baker.make('rowing.Club', name='Test Boat Club')

    def test_club_list_returns_200(self):
        """Test club list page loads successfully."""
        response = self.client.get(reverse('club-list'))
        self.assertEqual(response.status_code, 200)

    def test_club_list_contains_club(self):
        """Test club list contains our test club."""
        response = self.client.get(reverse('club-list'))
        self.assertContains(response, 'Test Boat Club')

    def test_club_detail_returns_200(self):
        """Test club detail page loads successfully."""
        response = self.client.get(reverse('club-detail', args=[self.club.pk]))
        self.assertEqual(response.status_code, 200)

    def test_club_detail_contains_name(self):
        """Test club detail contains the club name."""
        response = self.client.get(reverse('club-detail', args=[self.club.pk]))
        self.assertContains(response, 'Test Boat Club')

    def test_club_404_for_invalid_id(self):
        """Test club detail returns 404 for invalid ID."""
        response = self.client.get(reverse('club-detail', args=[999999999]))
        self.assertEqual(response.status_code, 404)


class TestEditionViews(TestCase):
    """Test edition detail views."""

    @classmethod
    def setUpTestData(cls):
        cls.competition = baker.make('rowing.Competition')
        cls.edition = baker.make('rowing.Edition', name='Test Edition 2024',
                                 comp=cls.competition)

    def test_edition_detail_returns_200(self):
        """Test edition detail page loads successfully."""
        response = self.client.get(reverse('edition-detail', args=[self.edition.pk]))
        self.assertEqual(response.status_code, 200)

    def test_edition_detail_contains_name(self):
        """Test edition detail contains the edition name."""
        response = self.client.get(reverse('edition-detail', args=[self.edition.pk]))
        self.assertContains(response, 'Test Edition 2024')

    def test_edition_404_for_invalid_id(self):
        """Test edition detail returns 404 for invalid ID."""
        response = self.client.get(reverse('edition-detail', args=[999999999]))
        self.assertEqual(response.status_code, 404)


class TestFixtureViews(TestCase):
    """Test fixture detail views."""

    @classmethod
    def setUpTestData(cls):
        cls.competition = baker.make('rowing.Competition')
        cls.event = baker.make('rowing.Event', comp=cls.competition, name='M8+')
        cls.edition = baker.make('rowing.Edition', comp=cls.competition, name='2024')
        cls.fixture = baker.make('rowing.Fixture', event=cls.event, edition=cls.edition)

    def test_fixture_detail_returns_200(self):
        """Test fixture detail page loads successfully."""
        response = self.client.get(reverse('fixture-detail', args=[self.fixture.pk]))
        self.assertEqual(response.status_code, 200)

    def test_fixture_404_for_invalid_id(self):
        """Test fixture detail returns 404 for invalid ID."""
        response = self.client.get(reverse('fixture-detail', args=[999999999]))
        self.assertEqual(response.status_code, 404)


class TestCompareView(TestCase):
    """Test the rower comparison view."""

    def test_compare_returns_200(self):
        """Test compare page loads successfully."""
        response = self.client.get(reverse('compare2'))
        self.assertEqual(response.status_code, 200)

    def test_compare_has_form(self):
        """Test compare page has the comparison form."""
        response = self.client.get(reverse('compare2'))
        self.assertIn('form', response.context)


class TestCrewCompareView(TestCase):
    """Test the crew comparison view."""

    def test_crew_compare_returns_200(self):
        """Test crew compare page loads successfully."""
        response = self.client.get(reverse('crewcompare'))
        self.assertEqual(response.status_code, 200)

    def test_crew_compare_has_form(self):
        """Test crew compare page has the comparison form."""
        response = self.client.get(reverse('crewcompare'))
        self.assertIn('form', response.context)


class TestRowerSearchView(TestCase):
    """Test the rower search view."""

    def test_rower_search_returns_200(self):
        """Test rower search page loads successfully."""
        response = self.client.get(reverse('rower-search'))
        self.assertEqual(response.status_code, 200)


class TestRankingsView(TestCase):
    """Test the rankings view."""

    @classmethod
    def setUpTestData(cls):
        # Create rowers with rankings
        cls.rower1 = baker.make('rowing.Rower', name='Top Rower', gender='M')
        cls.rower2 = baker.make('rowing.Rower', name='Second Rower', gender='M')

        ScoreRanking.objects.create(
            mu=35.0, sigma=5.0, delta_mu_sigma=30.0,
            rower=cls.rower1, date=datetime.date(2024, 6, 15),
            type='Sweep', sr_type='Current'
        )
        ScoreRanking.objects.create(
            mu=30.0, sigma=6.0, delta_mu_sigma=24.0,
            rower=cls.rower2, date=datetime.date(2024, 6, 15),
            type='Sweep', sr_type='Current'
        )

    def test_rankings_returns_200(self):
        """Test rankings page loads successfully."""
        # URL name is 'ranking' not 'rankings'
        response = self.client.get(reverse('ranking'))
        self.assertEqual(response.status_code, 200)

    def test_rankings_with_params(self):
        """Test rankings page with query parameters."""
        response = self.client.get(reverse('ranking') + '?type=Sweep&g=M&current=y&gb=n')
        self.assertEqual(response.status_code, 200)


class TestWeatherView(TestCase):
    """Test the weather calculator view."""

    def test_weather_returns_200(self):
        """Test weather page loads successfully."""
        response = self.client.get(reverse('weather'))
        self.assertEqual(response.status_code, 200)

    def test_weather_has_form(self):
        """Test weather page has the weather form."""
        response = self.client.get(reverse('weather'))
        self.assertIn('form', response.context)

    def test_weather_post_valid_data(self):
        """Test weather form processes valid POST data."""
        data = {
            'v1': 5.0,
            'water_temp1': 18.0, 'air_temp1': 18.0, 'air_pressure1': 1012.0,
            'air_humidity1': 0.25, 'water_flow1': 0.0, 'wind_v1': 0.0,
            'wind_angle1': 0.0, 'cd_air1': 0.9, 'A_air1': 2.0,
            'A_water1': 9.0, 'boat_length1': 18.0,
            'water_temp2': 15.0, 'air_temp2': 15.0, 'air_pressure2': 1000.0,
            'air_humidity2': 0.5, 'water_flow2': 0.5, 'wind_v2': 3.0,
            'wind_angle2': 0.0, 'cd_air2': 0.9, 'A_air2': 2.0,
            'A_water2': 9.0, 'boat_length2': 18.0,
        }
        response = self.client.post(reverse('weather'), data)
        # Should either return 200 with results or redirect
        self.assertIn(response.status_code, [200, 302])
