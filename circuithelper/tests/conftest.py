"""
Pytest configuration and fixtures for NetBox Circuit Manager tests.
"""

import pytest
from django.contrib.auth import get_user_model
from circuits.models import Provider, ProviderAccount, CircuitType, Circuit
from tenancy.models import Tenant


User = get_user_model()


@pytest.fixture
def test_user(db):
    """Create a test user."""
    return User.objects.create_user(
        username='testuser',
        password='testpass123',
        email='test@example.com'
    )


@pytest.fixture
def admin_user(db):
    """Create an admin user."""
    return User.objects.create_superuser(
        username='admin',
        password='admin123',
        email='admin@example.com'
    )


@pytest.fixture
def provider(db):
    """Create a test provider."""
    return Provider.objects.create(
        name='Test Provider',
        slug='test-provider'
    )


@pytest.fixture
def circuit_type(db):
    """Create a test circuit type."""
    return CircuitType.objects.create(
        name='Internet',
        slug='internet'
    )


@pytest.fixture
def circuit(db, provider, circuit_type):
    """Create a test circuit."""
    return Circuit.objects.create(
        cid='TEST-CIRCUIT-001',
        provider=provider,
        type=circuit_type,
        status='active'
    )


@pytest.fixture
def tenant(db):
    """Create a test tenant."""
    return Tenant.objects.create(
        name='Test Tenant',
        slug='test-tenant'
    )


@pytest.fixture
def api_client():
    """Create an API client for testing."""
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def authenticated_api_client(api_client, admin_user):
    """Create an authenticated API client."""
    api_client.force_authenticate(user=admin_user)
    return api_client
