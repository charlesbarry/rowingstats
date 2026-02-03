"""
Pytest configuration and shared fixtures for rowingstats tests.

This file is automatically loaded by pytest and provides:
- Django test database configuration
- Shared fixtures for common test objects
- Helper utilities for testing
"""
import pytest
from django.test import Client


@pytest.fixture
def client():
    """Provide a Django test client."""
    return Client()


@pytest.fixture
def authenticated_client(client, django_user_model):
    """Provide an authenticated Django test client."""
    user = django_user_model.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )
    client.force_login(user)
    return client


@pytest.fixture
def sample_rower(db):
    """Create a sample rower for testing."""
    from model_bakery import baker
    return baker.make('rowing.Rower')


@pytest.fixture
def sample_competition(db):
    """Create a sample competition for testing."""
    from model_bakery import baker
    return baker.make('rowing.Competition')


@pytest.fixture
def sample_race(db):
    """Create a sample race with related objects for testing."""
    from model_bakery import baker
    return baker.make('rowing.Race')


@pytest.fixture
def sample_club(db):
    """Create a sample club for testing."""
    from model_bakery import baker
    return baker.make('rowing.Club')


@pytest.fixture
def sample_result(db):
    """Create a sample result with crew for testing."""
    from model_bakery import baker
    return baker.make('rowing.Result')


@pytest.fixture
def sample_edition(db):
    """Create a sample edition for testing."""
    from model_bakery import baker
    return baker.make('rowing.Edition')


@pytest.fixture
def sample_fixture(db):
    """Create a sample fixture for testing."""
    from model_bakery import baker
    return baker.make('rowing.Fixture')


@pytest.fixture
def sample_score(db):
    """Create a sample score for testing."""
    from model_bakery import baker
    return baker.make('rowing.Score')


@pytest.fixture
def sample_article(db):
    """Create a sample blog article for testing."""
    from model_bakery import baker
    return baker.make('blog.Article')


# Weather calculation fixtures
@pytest.fixture
def default_weather_params():
    """Default weather parameters for testing."""
    return {
        'water_temp': 18.0,
        'air_temp': 18.0,
        'air_pressure': 1012.0,
        'air_humidity': 0.25,
        'water_flow': 0.0,
        'wind_v': 0.0,
        'wind_angle': 0,
        'cd_air': 0.9,
        'A_air': 2,
        'A_water': 9.0,
        'boat_length': 18.0,
    }


@pytest.fixture
def single_scull_params():
    """Weather parameters sized for a single scull."""
    return {
        'water_temp': 18.0,
        'air_temp': 18.0,
        'air_pressure': 1012.0,
        'air_humidity': 0.25,
        'water_flow': 0.0,
        'wind_v': 0.0,
        'wind_angle': 0,
        'cd_air': 0.9,
        'A_air': 0.8,
        'A_water': 2.5,
        'boat_length': 8.2,
    }


@pytest.fixture
def eight_params():
    """Weather parameters sized for an eight."""
    return {
        'water_temp': 18.0,
        'air_temp': 18.0,
        'air_pressure': 1012.0,
        'air_humidity': 0.25,
        'water_flow': 0.0,
        'wind_v': 0.0,
        'wind_angle': 0,
        'cd_air': 0.9,
        'A_air': 2.0,
        'A_water': 9.0,
        'boat_length': 18.0,
    }
