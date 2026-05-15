"""
Basic test to verify test infrastructure is set up correctly.
"""

import pytest
from django.conf import settings


@pytest.mark.unit
def test_django_settings_configured():
    """Test that Django settings are properly configured."""
    assert settings.configured
    assert settings.DATABASES is not None


@pytest.mark.unit
def test_email_backend_configured():
    """Test that email backend is configured for testing."""
    assert "locmem" in settings.EMAIL_BACKEND


@pytest.mark.unit
def test_fixtures_import():
    """Test that fixtures can be imported."""
    from tests.fixtures import factories

    assert factories is not None


@pytest.mark.unit
def test_basic_math():
    """Basic sanity check test."""
    assert 1 + 1 == 2
