"""
Tests for provider API integration framework.
"""

import pytest
from unittest.mock import Mock, patch
from decimal import Decimal

from circuithelper.models import ProviderAPIConfig, CircuitCost
from circuithelper.providers.base import BaseProviderSync
from circuithelper.providers.registry import ProviderRegistry
from circuithelper.providers.lumen import LumenProviderSync


class MockProviderSync(BaseProviderSync):
    """Mock provider for testing."""

    provider_name = "mock_provider"

    def __init__(self, api_config):
        super().__init__(api_config)
        self.authenticated = False
        self.circuits_data = []
        self.circuit_details = {}

    def authenticate(self):
        """Mock authentication."""
        self.authenticated = True
        return True

    def get_circuits(self):
        """Mock get circuits."""
        return self.circuits_data

    def get_circuit_details(self, circuit_id):
        """Mock get circuit details."""
        return self.circuit_details.get(circuit_id, {})

    def sync_circuit_costs(self, circuit, provider_data):
        """Mock sync circuit costs."""
        CircuitCost.objects.update_or_create(
            circuit=circuit, defaults={"mrc": Decimal("100.00"), "currency": "USD"}
        )
        return True


@pytest.mark.django_db
class TestProviderRegistry:
    """Test ProviderRegistry functionality."""

    def test_register_provider(self):
        """Test registering a provider."""
        registry = ProviderRegistry()
        registry.register("test", MockProviderSync)

        assert registry.get("test") == MockProviderSync

    def test_get_nonexistent_provider(self):
        """Test getting a provider that doesn't exist."""
        registry = ProviderRegistry()
        result = registry.get("nonexistent")

        assert result is None

    def test_unregister_provider(self):
        """Test unregistering a provider."""
        registry = ProviderRegistry()
        registry.register("test", MockProviderSync)
        registry.unregister("test")

        assert registry.get("test") is None

    def test_get_all_providers(self):
        """Test getting all registered providers."""
        registry = ProviderRegistry()
        registry.register("test1", MockProviderSync)
        registry.register("test2", MockProviderSync)

        all_providers = registry.get_all()

        assert len(all_providers) == 2
        assert "test1" in all_providers
        assert "test2" in all_providers


@pytest.mark.django_db
class TestBaseProviderSync:
    """Test BaseProviderSync functionality."""

    def test_provider_initialization(self, provider):
        """Test initializing a provider sync."""
        config = ProviderAPIConfig.objects.create(
            provider=provider,
            provider_type="mock_provider",
            api_endpoint="https://api.example.com",
            api_key="test_key",
            api_secret="test_secret",
        )

        sync = MockProviderSync(config)

        assert sync.config == config
        assert sync.api_endpoint == "https://api.example.com"
        assert sync.api_key == "test_key"
        assert sync.api_secret == "test_secret"

    def test_session_setup(self, provider):
        """Test session is set up with auth headers."""
        config = ProviderAPIConfig.objects.create(
            provider=provider,
            provider_type="mock_provider",
            api_endpoint="https://api.example.com",
            api_key="test_key",
        )

        sync = MockProviderSync(config)

        assert "Authorization" in sync.session.headers
        assert "Bearer test_key" in sync.session.headers["Authorization"]

    def test_authenticate(self, provider):
        """Test authentication method."""
        config = ProviderAPIConfig.objects.create(
            provider=provider, provider_type="mock_provider", api_endpoint="https://api.example.com"
        )

        sync = MockProviderSync(config)
        result = sync.authenticate()

        assert result is True
        assert sync.authenticated is True

    def test_match_circuit(self, provider, circuit):
        """Test circuit matching logic."""
        config = ProviderAPIConfig.objects.create(
            provider=provider, provider_type="mock_provider", api_endpoint="https://api.example.com"
        )

        sync = MockProviderSync(config)
        provider_data = {"cid": circuit.cid}

        matched_circuit = sync._match_circuit(provider_data)

        assert matched_circuit == circuit

    def test_match_circuit_not_found(self, provider):
        """Test circuit matching when circuit doesn't exist."""
        config = ProviderAPIConfig.objects.create(
            provider=provider, provider_type="mock_provider", api_endpoint="https://api.example.com"
        )

        sync = MockProviderSync(config)
        provider_data = {"cid": "NONEXISTENT"}

        matched_circuit = sync._match_circuit(provider_data)

        assert matched_circuit is None

    def test_test_connection_success(self, provider):
        """Test connection test when successful."""
        config = ProviderAPIConfig.objects.create(
            provider=provider, provider_type="mock_provider", api_endpoint="https://api.example.com"
        )

        sync = MockProviderSync(config)
        result = sync.test_connection()

        assert result["success"] is True
        assert "Connection successful" in result["message"]
        assert result["response_time"] >= 0

    def test_sync_all(self, provider, circuit):
        """Test full synchronization."""
        config = ProviderAPIConfig.objects.create(
            provider=provider,
            provider_type="mock_provider",
            api_endpoint="https://api.example.com",
            sync_enabled=True,
        )

        sync = MockProviderSync(config)
        sync.circuits_data = [{"id": "circuit-1", "cid": circuit.cid}]
        sync.circuit_details = {"circuit-1": {"billing": {"mrc": 100.00}}}

        stats = sync.sync_all()

        assert stats["total"] == 1
        assert stats["success"] == 1
        assert stats["failed"] == 0
        assert len(stats["errors"]) == 0

        # Verify cost was synced
        assert CircuitCost.objects.filter(circuit=circuit).exists()

    def test_sync_all_with_failures(self, provider, circuit):
        """Test sync with some failures."""
        config = ProviderAPIConfig.objects.create(
            provider=provider, provider_type="mock_provider", api_endpoint="https://api.example.com"
        )

        sync = MockProviderSync(config)
        sync.circuits_data = [
            {"id": "circuit-1", "cid": circuit.cid},
            {"id": "circuit-2", "cid": "NONEXISTENT"},  # Will fail
        ]
        sync.circuit_details = {
            "circuit-1": {"billing": {"mrc": 100.00}},
            "circuit-2": {"billing": {"mrc": 200.00}},
        }

        stats = sync.sync_all()

        assert stats["total"] == 2
        assert stats["success"] == 1
        assert stats["failed"] == 1
        assert len(stats["errors"]) > 0


@pytest.mark.django_db
class TestLumenProviderSync:
    """Test Lumen provider integration."""

    def test_lumen_provider_initialization(self, provider):
        """Test initializing Lumen provider."""
        config = ProviderAPIConfig.objects.create(
            provider=provider,
            provider_type="lumen",
            api_endpoint="https://api.lumen.com",
            api_key="test_key",
            api_secret="test_secret",
        )

        sync = LumenProviderSync(config)

        assert sync.provider_name == "lumen"
        assert sync.api_endpoint == "https://api.lumen.com"

    @patch("requests.Session.post")
    def test_lumen_authenticate(self, mock_post, provider):
        """Test Lumen authentication."""
        config = ProviderAPIConfig.objects.create(
            provider=provider,
            provider_type="lumen",
            api_endpoint="https://api.lumen.com",
            api_key="test_key",
            api_secret="test_secret",
        )

        # Mock successful auth response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"access_token": "token123"}
        mock_post.return_value = mock_response

        sync = LumenProviderSync(config)
        result = sync.authenticate()

        assert result is True
        assert "Bearer token123" in sync.session.headers["Authorization"]

    @patch("requests.Session.get")
    def test_lumen_get_circuits(self, mock_get, provider):
        """Test getting circuits from Lumen API."""
        config = ProviderAPIConfig.objects.create(
            provider=provider, provider_type="lumen", api_endpoint="https://api.lumen.com"
        )

        # Mock circuits response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "circuits": [
                {"id": "circuit-1", "cid": "TEST-001"},
                {"id": "circuit-2", "cid": "TEST-002"},
            ]
        }
        mock_get.return_value = mock_response

        sync = LumenProviderSync(config)
        circuits = sync.get_circuits()

        assert len(circuits) == 2
        assert circuits[0]["cid"] == "TEST-001"

    @patch("requests.Session.get")
    def test_lumen_get_circuit_details(self, mock_get, provider):
        """Test getting circuit details from Lumen API."""
        config = ProviderAPIConfig.objects.create(
            provider=provider, provider_type="lumen", api_endpoint="https://api.lumen.com"
        )

        # Mock circuit details response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "circuit-1",
            "billing": {"monthly_recurring_charge": 150.00, "non_recurring_charge": 500.00},
        }
        mock_get.return_value = mock_response

        sync = LumenProviderSync(config)
        details = sync.get_circuit_details("circuit-1")

        assert details["billing"]["monthly_recurring_charge"] == 150.00

    def test_lumen_sync_circuit_costs(self, provider, circuit):
        """Test syncing circuit costs from Lumen data."""
        config = ProviderAPIConfig.objects.create(
            provider=provider, provider_type="lumen", api_endpoint="https://api.lumen.com"
        )

        provider_data = {
            "billing": {
                "non_recurring_charge": 500.00,
                "monthly_recurring_charge": 150.00,
                "currency": "USD",
                "account_number": "ACC-123",
            }
        }

        sync = LumenProviderSync(config)
        result = sync.sync_circuit_costs(circuit, provider_data)

        assert result is True

        cost = CircuitCost.objects.get(circuit=circuit)
        assert cost.nrc == Decimal("500.00")
        assert cost.mrc == Decimal("150.00")
        assert cost.currency == "USD"

    def test_lumen_ticket_status_mapping(self, provider):
        """Test ticket status mapping."""
        config = ProviderAPIConfig.objects.create(
            provider=provider, provider_type="lumen", api_endpoint="https://api.lumen.com"
        )

        sync = LumenProviderSync(config)

        assert sync._map_ticket_status("new") == "open"
        assert sync._map_ticket_status("working") == "in_progress"
        assert sync._map_ticket_status("pending_customer") == "pending"
        assert sync._map_ticket_status("resolved") == "resolved"

    def test_lumen_ticket_priority_mapping(self, provider):
        """Test ticket priority mapping."""
        config = ProviderAPIConfig.objects.create(
            provider=provider, provider_type="lumen", api_endpoint="https://api.lumen.com"
        )

        sync = LumenProviderSync(config)

        assert sync._map_ticket_priority("p1") == "critical"
        assert sync._map_ticket_priority("p2") == "high"
        assert sync._map_ticket_priority("p3") == "medium"
        assert sync._map_ticket_priority("p4") == "low"
