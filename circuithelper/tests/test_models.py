"""
Tests for NetBox Circuit Manager models.
"""

from datetime import date, datetime
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile

from circuithelper.models import (
    CircuitContract,
    CircuitCost,
    CircuitPath,
    CircuitTicket,
    ProviderAPIConfig,
)


@pytest.mark.django_db
class TestCircuitCost:
    """Test CircuitCost model."""

    def test_create_circuit_cost(self, circuit):
        """Test creating a circuit cost."""
        cost = CircuitCost.objects.create(
            circuit=circuit,
            nrc=Decimal("500.00"),
            mrc=Decimal("150.00"),
            currency="USD",
            billing_account="ACC-123456",
        )

        assert cost.circuit == circuit
        assert cost.nrc == Decimal("500.00")
        assert cost.mrc == Decimal("150.00")
        assert cost.currency == "USD"
        assert cost.billing_account == "ACC-123456"

    def test_circuit_cost_string_representation(self, circuit):
        """Test __str__ method."""
        cost = CircuitCost.objects.create(circuit=circuit, mrc=Decimal("150.00"), currency="USD")
        assert "TEST-CIRCUIT-001" in str(cost)
        assert "MRC: 150.00 USD" in str(cost)

    def test_circuit_cost_unique_per_circuit(self, circuit):
        """Test that only one cost record exists per circuit."""
        CircuitCost.objects.create(circuit=circuit, nrc=Decimal("500.00"), mrc=Decimal("150.00"))

        # Creating another should fail due to OneToOne relationship
        with pytest.raises(Exception):
            CircuitCost.objects.create(
                circuit=circuit, nrc=Decimal("600.00"), mrc=Decimal("200.00")
            )

    def test_circuit_cost_negative_validation(self, circuit):
        """Test that negative costs are rejected."""
        with pytest.raises(ValidationError):
            cost = CircuitCost(circuit=circuit, nrc=Decimal("-500.00"), mrc=Decimal("150.00"))
            cost.full_clean()

    def test_circuit_cost_optional_fields(self, circuit):
        """Test that NRC and MRC are optional."""
        cost = CircuitCost.objects.create(circuit=circuit, currency="EUR")
        assert cost.nrc is None
        assert cost.mrc is None
        assert cost.currency == "EUR"


@pytest.mark.django_db
class TestCircuitContract:
    """Test CircuitContract model."""

    def test_create_circuit_contract(self, circuit):
        """Test creating a circuit contract."""
        contract = CircuitContract.objects.create(
            circuit=circuit,
            contract_number="CONTRACT-2024-001",
            start_date=date(2024, 1, 1),
            end_date=date(2027, 12, 31),
            term_months=48,
            auto_renew=True,
            renewal_notice_days=90,
            early_termination_fee=Decimal("5000.00"),
        )

        assert contract.circuit == circuit
        assert contract.contract_number == "CONTRACT-2024-001"
        assert contract.term_months == 48
        assert contract.auto_renew is True

    def test_circuit_contract_string_representation(self, circuit):
        """Test __str__ method."""
        contract = CircuitContract.objects.create(
            circuit=circuit, contract_number="CONTRACT-2024-001", start_date=date(2024, 1, 1)
        )
        assert "TEST-CIRCUIT-001" in str(contract)
        assert "CONTRACT-2024-001" in str(contract)

    def test_multiple_contracts_per_circuit(self, circuit):
        """Test that a circuit can have multiple contracts."""
        _contract1 = CircuitContract.objects.create(
            circuit=circuit,
            contract_number="CONTRACT-2024-001",
            start_date=date(2024, 1, 1),
            end_date=date(2025, 12, 31),
        )
        _contract2 = CircuitContract.objects.create(
            circuit=circuit,
            contract_number="CONTRACT-2026-001",
            start_date=date(2026, 1, 1),
            end_date=date(2029, 12, 31),
        )

        assert circuit.contracts.count() == 2

    def test_contract_file_upload(self, circuit):
        """Test uploading a contract file."""
        file_content = b"PDF file content"
        uploaded_file = SimpleUploadedFile(
            "contract.pdf", file_content, content_type="application/pdf"
        )

        contract = CircuitContract.objects.create(
            circuit=circuit,
            contract_number="CONTRACT-2024-001",
            start_date=date(2024, 1, 1),
            contract_file=uploaded_file,
        )

        assert contract.contract_file is not None
        assert "contract.pdf" in contract.contract_file.name


@pytest.mark.django_db
class TestCircuitTicket:
    """Test CircuitTicket model."""

    def test_create_circuit_ticket(self, circuit):
        """Test creating a circuit ticket."""
        ticket = CircuitTicket.objects.create(
            circuit=circuit,
            ticket_number="TKT-123456",
            subject="Circuit down",
            status="open",
            priority="critical",
            description="Circuit is experiencing packet loss",
            external_url="https://provider.com/tickets/123456",
        )

        assert ticket.circuit == circuit
        assert ticket.ticket_number == "TKT-123456"
        assert ticket.status == "open"
        assert ticket.priority == "critical"

    def test_circuit_ticket_string_representation(self, circuit):
        """Test __str__ method."""
        ticket = CircuitTicket.objects.create(
            circuit=circuit, ticket_number="TKT-123456", subject="Circuit down", description="Issue"
        )
        assert "TKT-123456" in str(ticket)
        assert "TEST-CIRCUIT-001" in str(ticket)

    def test_ticket_unique_number(self, circuit):
        """Test that ticket numbers must be unique."""
        CircuitTicket.objects.create(
            circuit=circuit,
            ticket_number="TKT-123456",
            subject="Issue 1",
            description="Description 1",
        )

        with pytest.raises(Exception):
            CircuitTicket.objects.create(
                circuit=circuit,
                ticket_number="TKT-123456",  # Duplicate
                subject="Issue 2",
                description="Description 2",
            )

    def test_multiple_tickets_per_circuit(self, circuit):
        """Test that a circuit can have multiple tickets."""
        CircuitTicket.objects.create(
            circuit=circuit, ticket_number="TKT-001", subject="Issue 1", description="Description 1"
        )
        CircuitTicket.objects.create(
            circuit=circuit, ticket_number="TKT-002", subject="Issue 2", description="Description 2"
        )

        assert circuit.tickets.count() == 2

    def test_ticket_status_choices(self, circuit):
        """Test ticket status choices."""
        ticket = CircuitTicket.objects.create(
            circuit=circuit,
            ticket_number="TKT-123",
            subject="Test",
            description="Test",
            status="in_progress",
        )
        assert ticket.status == "in_progress"

    def test_ticket_priority_choices(self, circuit):
        """Test ticket priority choices."""
        ticket = CircuitTicket.objects.create(
            circuit=circuit,
            ticket_number="TKT-123",
            subject="Test",
            description="Test",
            priority="high",
        )
        assert ticket.priority == "high"


@pytest.mark.django_db
class TestCircuitPath:
    """Test CircuitPath model."""

    def test_create_circuit_path(self, circuit):
        """Test creating a circuit path."""
        path = CircuitPath.objects.create(
            circuit=circuit,
            map_center_lat=Decimal("37.7749"),
            map_center_lon=Decimal("-122.4194"),
            map_zoom=10,
            path_distance_km=Decimal("25.5"),
            path_notes="Fiber path through downtown",
        )

        assert path.circuit == circuit
        assert path.map_center_lat == Decimal("37.7749")
        assert path.map_center_lon == Decimal("-122.4194")
        assert path.path_distance_km == Decimal("25.5")

    def test_circuit_path_string_representation(self, circuit):
        """Test __str__ method."""
        path = CircuitPath.objects.create(circuit=circuit, map_zoom=10)
        assert "TEST-CIRCUIT-001" in str(path)
        assert "Path" in str(path)

    def test_circuit_path_unique_per_circuit(self, circuit):
        """Test that only one path exists per circuit."""
        CircuitPath.objects.create(circuit=circuit, map_zoom=10)

        with pytest.raises(Exception):
            CircuitPath.objects.create(circuit=circuit, map_zoom=12)

    def test_kmz_file_upload(self, circuit):
        """Test uploading a KMZ file."""
        file_content = b"KMZ file content"
        uploaded_file = SimpleUploadedFile(
            "circuit_path.kmz", file_content, content_type="application/vnd.google-earth.kmz"
        )

        path = CircuitPath.objects.create(circuit=circuit, kmz_file=uploaded_file, map_zoom=10)

        assert path.kmz_file is not None
        assert "circuit_path.kmz" in path.kmz_file.name

    def test_geojson_data_storage(self, circuit):
        """Test storing GeoJSON data."""
        geojson = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {"type": "LineString", "coordinates": [[0, 0], [1, 1]]},
                    "properties": {"name": "Test Path"},
                }
            ],
        }

        path = CircuitPath.objects.create(circuit=circuit, geojson_data=geojson, map_zoom=10)

        assert path.geojson_data["type"] == "FeatureCollection"
        assert len(path.geojson_data["features"]) == 1


@pytest.mark.django_db
class TestProviderAPIConfig:
    """Test ProviderAPIConfig model."""

    def test_create_provider_api_config(self, provider):
        """Test creating a provider API configuration."""
        config = ProviderAPIConfig.objects.create(
            provider=provider,
            provider_type="lumen",
            api_endpoint="https://api.lumen.com",
            api_key="test_key_123",
            api_secret="test_secret_456",
            sync_enabled=True,
            sync_interval_hours=24,
        )

        assert config.provider == provider
        assert config.provider_type == "lumen"
        assert config.api_endpoint == "https://api.lumen.com"
        assert config.sync_enabled is True
        assert config.sync_interval_hours == 24

    def test_provider_api_config_string_representation(self, provider):
        """Test __str__ method."""
        config = ProviderAPIConfig.objects.create(
            provider=provider, provider_type="lumen", api_endpoint="https://api.lumen.com"
        )
        assert "Test Provider" in str(config)
        assert "lumen" in str(config)

    def test_provider_api_config_unique_constraint(self, provider):
        """Test unique constraint on provider + provider_type."""
        ProviderAPIConfig.objects.create(
            provider=provider, provider_type="lumen", api_endpoint="https://api.lumen.com"
        )

        with pytest.raises(Exception):
            ProviderAPIConfig.objects.create(
                provider=provider,
                provider_type="lumen",  # Duplicate combination
                api_endpoint="https://api2.lumen.com",
            )

    def test_multiple_provider_types_per_provider(self, provider):
        """Test that a provider can have multiple API configs for different types."""
        _config1 = ProviderAPIConfig.objects.create(
            provider=provider, provider_type="lumen", api_endpoint="https://api1.lumen.com"
        )
        _config2 = ProviderAPIConfig.objects.create(
            provider=provider, provider_type="custom", api_endpoint="https://api2.custom.com"
        )

        assert provider.api_configs.count() == 2

    def test_sync_status_tracking(self, provider):
        """Test sync status and timestamp tracking."""
        config = ProviderAPIConfig.objects.create(
            provider=provider,
            provider_type="lumen",
            api_endpoint="https://api.lumen.com",
            sync_enabled=True,
            last_sync=datetime.now(),
            sync_status="Success: 10/10 circuits synced",
        )

        assert config.last_sync is not None
        assert "Success" in config.sync_status
