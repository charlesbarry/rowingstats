"""
Unit tests for rowing/forms.py

Tests form validation, field requirements, and form initialization
for all forms used in the rowing application.
"""
import pytest
from django.test import TestCase
from rowing.forms import (
    CompareForm, CrewCompareForm, WeatherForm, RankingForm,
    RowerForm, CompetitionForm, RowerCorrectForm, RowerMergeForm,
    ResultCorrectForm, FixtureEditionForm, FixtureEventForm
)


class TestCompareForm(TestCase):
    """Test CompareForm for rower comparison."""

    def test_compare_form_fields(self):
        """Test CompareForm has expected fields."""
        form = CompareForm()
        self.assertIn('rower1', form.fields)
        self.assertIn('rower2', form.fields)
        self.assertIn('type', form.fields)

    def test_compare_form_type_choices(self):
        """Test CompareForm type field has correct choices."""
        form = CompareForm()
        type_field = form.fields['type']
        choice_values = [c[0] for c in type_field.choices]
        self.assertIn('Sweep', choice_values)
        self.assertIn('Sculling', choice_values)
        self.assertIn('Lwt Sweep', choice_values)
        self.assertIn('Lwt Sculling', choice_values)

    def test_compare_form_type_required(self):
        """Test type field is required."""
        form = CompareForm()
        self.assertTrue(form.fields['type'].required)

    def test_compare_form_rowers_optional(self):
        """Test rower fields are optional."""
        form = CompareForm()
        self.assertFalse(form.fields['rower1'].required)
        self.assertFalse(form.fields['rower2'].required)


class TestCrewCompareForm(TestCase):
    """Test CrewCompareForm for crew comparison."""

    def test_crew_compare_form_fields(self):
        """Test CrewCompareForm has expected fields."""
        form = CrewCompareForm()
        self.assertIn('crew1', form.fields)
        self.assertIn('crew2', form.fields)
        self.assertIn('type', form.fields)

    def test_crew_compare_form_type_choices(self):
        """Test CrewCompareForm type field has correct choices."""
        form = CrewCompareForm()
        type_field = form.fields['type']
        choice_values = [c[0] for c in type_field.choices]
        self.assertIn('Sweep', choice_values)
        self.assertIn('Sculling', choice_values)

    def test_crew_compare_crews_optional(self):
        """Test crew fields are optional."""
        form = CrewCompareForm()
        self.assertFalse(form.fields['crew1'].required)
        self.assertFalse(form.fields['crew2'].required)


class TestWeatherForm(TestCase):
    """Test WeatherForm for weather calculation inputs."""

    def test_weather_form_has_all_fields(self):
        """Test WeatherForm has all 23 expected fields."""
        form = WeatherForm()
        expected_fields = [
            'v1', 'water_temp1', 'air_temp1', 'air_pressure1',
            'air_humidity1', 'water_flow1', 'wind_v1', 'wind_angle1',
            'cd_air1', 'A_air1', 'A_water1', 'boat_length1',
            'water_temp2', 'air_temp2', 'air_pressure2',
            'air_humidity2', 'water_flow2', 'wind_v2', 'wind_angle2',
            'cd_air2', 'A_air2', 'A_water2', 'boat_length2'
        ]
        for field_name in expected_fields:
            self.assertIn(field_name, form.fields,
                         f"Missing field: {field_name}")

    def test_weather_form_all_fields_required(self):
        """Test all weather form fields are required."""
        form = WeatherForm()
        for field_name, field in form.fields.items():
            self.assertTrue(field.required,
                           f"Field {field_name} should be required")

    def test_weather_form_fields_are_floats(self):
        """Test all weather form fields accept float values."""
        form = WeatherForm()
        for field_name, field in form.fields.items():
            self.assertEqual(field.__class__.__name__, 'FloatField',
                            f"Field {field_name} should be FloatField")

    def test_weather_form_valid_data(self):
        """Test WeatherForm accepts valid data."""
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
        form = WeatherForm(data=data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_weather_form_rejects_non_numeric(self):
        """Test WeatherForm rejects non-numeric input."""
        data = {
            'v1': 'not a number',
            'water_temp1': 18.0, 'air_temp1': 18.0, 'air_pressure1': 1012.0,
            'air_humidity1': 0.25, 'water_flow1': 0.0, 'wind_v1': 0.0,
            'wind_angle1': 0.0, 'cd_air1': 0.9, 'A_air1': 2.0,
            'A_water1': 9.0, 'boat_length1': 18.0,
            'water_temp2': 15.0, 'air_temp2': 15.0, 'air_pressure2': 1000.0,
            'air_humidity2': 0.5, 'water_flow2': 0.5, 'wind_v2': 3.0,
            'wind_angle2': 0.0, 'cd_air2': 0.9, 'A_air2': 2.0,
            'A_water2': 9.0, 'boat_length2': 18.0,
        }
        form = WeatherForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('v1', form.errors)


class TestRankingForm(TestCase):
    """Test RankingForm for rankings page filters."""

    def test_ranking_form_fields(self):
        """Test RankingForm has expected fields."""
        form = RankingForm()
        self.assertIn('type', form.fields)
        self.assertIn('g', form.fields)
        self.assertIn('current', form.fields)
        self.assertIn('gb', form.fields)

    def test_ranking_form_gender_choices(self):
        """Test gender field has correct choices."""
        form = RankingForm()
        g_field = form.fields['g']
        choice_values = [c[0] for c in g_field.choices]
        self.assertIn('M', choice_values)
        self.assertIn('W', choice_values)

    def test_ranking_form_current_choices(self):
        """Test current field has correct choices."""
        form = RankingForm()
        current_field = form.fields['current']
        choice_values = [c[0] for c in current_field.choices]
        self.assertIn('y', choice_values)
        self.assertIn('n', choice_values)

    def test_ranking_form_gb_choices(self):
        """Test gb field has correct choices."""
        form = RankingForm()
        gb_field = form.fields['gb']
        choice_values = [c[0] for c in gb_field.choices]
        self.assertIn('y', choice_values)
        self.assertIn('n', choice_values)

    def test_ranking_form_valid_data(self):
        """Test RankingForm accepts valid data."""
        data = {
            'type': 'Sweep',
            'g': 'M',
            'current': 'y',
            'gb': 'n'
        }
        form = RankingForm(data=data)
        self.assertTrue(form.is_valid(), form.errors)


class TestRowerForm(TestCase):
    """Test RowerForm for rower page filters."""

    def test_rower_form_fields(self):
        """Test RowerForm has expected fields."""
        form = RowerForm()
        self.assertIn('type', form.fields)

    def test_rower_form_type_choices(self):
        """Test type field has correct choices."""
        form = RowerForm()
        type_field = form.fields['type']
        choice_values = [c[0] for c in type_field.choices]
        self.assertIn('Sweep', choice_values)
        self.assertIn('Sculling', choice_values)


class TestCompetitionForm(TestCase):
    """Test CompetitionForm for competition filtering."""

    def test_competition_form_initialization(self):
        """Test CompetitionForm initializes with dynamic choices."""
        class_choices = [('', 'Any'), ('Senior', 'Senior')]
        event_choices = [('', 'Any'), ('M8+', 'Mens Eight')]
        year_choices = [('', 'Any'), ('2024', '2024')]

        form = CompetitionForm(class_choices, event_choices, year_choices)

        self.assertEqual(form.fields['raceclass'].choices, class_choices)
        self.assertEqual(form.fields['event'].choices, event_choices)
        self.assertEqual(form.fields['year'].choices, year_choices)

    def test_competition_form_type_includes_any(self):
        """Test type field includes 'Any' option."""
        form = CompetitionForm([], [], [])
        type_field = form.fields['type']
        choice_values = [c[0] for c in type_field.choices]
        self.assertIn('', choice_values)  # Empty string for 'Any'


class TestFixtureEditionForm(TestCase):
    """Test FixtureEditionForm for edition filtering."""

    def test_fixture_edition_form_initialization(self):
        """Test FixtureEditionForm initializes with dynamic choices."""
        edition_choices = [('', 'Any'), ('1', '2024 Olympics')]

        form = FixtureEditionForm(edition_choices)

        self.assertEqual(form.fields['edition'].choices, edition_choices)


class TestFixtureEventForm(TestCase):
    """Test FixtureEventForm for event filtering."""

    def test_fixture_event_form_initialization(self):
        """Test FixtureEventForm initializes with dynamic choices."""
        event_choices = [('', 'Any'), ('M8+', 'Mens Eight')]

        form = FixtureEventForm(event_choices)

        self.assertEqual(form.fields['event'].choices, event_choices)


class TestRowerCorrectForm(TestCase):
    """Test RowerCorrectForm for user corrections."""

    def test_rower_correct_form_fields(self):
        """Test RowerCorrectForm has expected fields."""
        form = RowerCorrectForm()
        self.assertIn('name', form.fields)
        self.assertIn('nationality', form.fields)
        self.assertIn('gender', form.fields)
        self.assertIn('your_name', form.fields)
        self.assertIn('your_email', form.fields)

    def test_rower_correct_form_contact_required(self):
        """Test contact fields are required."""
        form = RowerCorrectForm()
        self.assertTrue(form.fields['your_name'].required)
        self.assertTrue(form.fields['your_email'].required)

    def test_rower_correct_form_email_validation(self):
        """Test email field validates email format."""
        form = RowerCorrectForm()
        email_field = form.fields['your_email']
        self.assertEqual(email_field.min_length, 6)


class TestRowerMergeForm(TestCase):
    """Test RowerMergeForm for merging duplicate rowers."""

    def test_rower_merge_form_fields(self):
        """Test RowerMergeForm has expected fields."""
        form = RowerMergeForm()
        self.assertIn('merger', form.fields)
        self.assertIn('your_name', form.fields)
        self.assertIn('your_email', form.fields)

    def test_rower_merge_form_contact_required(self):
        """Test contact fields are required."""
        form = RowerMergeForm()
        self.assertTrue(form.fields['your_name'].required)
        self.assertTrue(form.fields['your_email'].required)


class TestResultCorrectForm(TestCase):
    """Test ResultCorrectForm for result corrections."""

    def test_result_correct_form_fields(self):
        """Test ResultCorrectForm has expected fields."""
        form = ResultCorrectForm()
        self.assertIn('crew', form.fields)
        self.assertIn('clubs', form.fields)
        self.assertIn('cox', form.fields)
        self.assertIn('flag', form.fields)
        self.assertIn('your_name', form.fields)
        self.assertIn('your_email', form.fields)

    def test_result_correct_form_contact_required(self):
        """Test contact fields are required."""
        form = ResultCorrectForm()
        self.assertTrue(form.fields['your_name'].required)
        self.assertTrue(form.fields['your_email'].required)

    def test_result_correct_form_crew_optional(self):
        """Test crew field is optional."""
        form = ResultCorrectForm()
        self.assertFalse(form.fields['crew'].required)
