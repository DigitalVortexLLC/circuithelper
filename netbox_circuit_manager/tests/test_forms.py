"""
Tests for NetBox Circuit Manager forms.
"""

import pytest
from decimal import Decimal
from datetime import date
from django.core.files.uploadedfile import SimpleUploadedFile

from netbox_circuit_manager.forms import (
    CircuitCostForm,
    CircuitContractForm,
    CircuitTicketForm,
    CircuitPathForm,
    ProviderAPIConfigForm
)


@pytest.mark.django_db
class TestCircuitCostForm:
    """Test CircuitCostForm validation."""

    def test_valid_circuit_cost_form(self, circuit):
        """Test form with valid data."""
        form_data = {
            'circuit': circuit.pk,
            'nrc': Decimal('500.00'),
            'mrc': Decimal('150.00'),
            'currency': 'USD',
            'billing_account': 'ACC-123'
        }
        form = CircuitCostForm(data=form_data)
        assert form.is_valid()

    def test_form_with_missing_circuit(self):
        """Test form validation fails without circuit."""
        form_data = {
            'mrc': Decimal('150.00'),
            'currency': 'USD'
        }
        form = CircuitCostForm(data=form_data)
        assert not form.is_valid()
        assert 'circuit' in form.errors

    def test_form_with_optional_fields(self, circuit):
        """Test form with only required fields."""
        form_data = {
            'circuit': circuit.pk,
            'currency': 'USD'
        }
        form = CircuitCostForm(data=form_data)
        assert form.is_valid()

    def test_form_decimal_validation(self, circuit):
        """Test decimal field validation."""
        form_data = {
            'circuit': circuit.pk,
            'mrc': 'invalid',
            'currency': 'USD'
        }
        form = CircuitCostForm(data=form_data)
        assert not form.is_valid()
        assert 'mrc' in form.errors


@pytest.mark.django_db
class TestCircuitContractForm:
    """Test CircuitContractForm validation."""

    def test_valid_circuit_contract_form(self, circuit):
        """Test form with valid data."""
        form_data = {
            'circuit': circuit.pk,
            'contract_number': 'CONTRACT-001',
            'start_date': date(2024, 1, 1),
            'end_date': date(2027, 12, 31),
            'term_months': 48,
            'auto_renew': True
        }
        form = CircuitContractForm(data=form_data)
        assert form.is_valid()

    def test_form_with_file_upload(self, circuit):
        """Test form with file upload."""
        file_content = b'PDF content'
        uploaded_file = SimpleUploadedFile(
            'contract.pdf',
            file_content,
            content_type='application/pdf'
        )

        form_data = {
            'circuit': circuit.pk,
            'contract_number': 'CONTRACT-001',
            'start_date': date(2024, 1, 1)
        }
        form = CircuitContractForm(
            data=form_data,
            files={'contract_file': uploaded_file}
        )
        assert form.is_valid()

    def test_form_date_validation(self, circuit):
        """Test date field validation."""
        form_data = {
            'circuit': circuit.pk,
            'contract_number': 'CONTRACT-001',
            'start_date': 'invalid-date'
        }
        form = CircuitContractForm(data=form_data)
        assert not form.is_valid()
        assert 'start_date' in form.errors

    def test_form_required_fields(self, circuit):
        """Test that required fields are validated."""
        form_data = {
            'circuit': circuit.pk
            # Missing required fields
        }
        form = CircuitContractForm(data=form_data)
        assert not form.is_valid()
        assert 'contract_number' in form.errors
        assert 'start_date' in form.errors


@pytest.mark.django_db
class TestCircuitTicketForm:
    """Test CircuitTicketForm validation."""

    def test_valid_circuit_ticket_form(self, circuit):
        """Test form with valid data."""
        form_data = {
            'circuit': circuit.pk,
            'ticket_number': 'TKT-123',
            'subject': 'Circuit issue',
            'status': 'open',
            'priority': 'high',
            'description': 'Circuit is down'
        }
        form = CircuitTicketForm(data=form_data)
        assert form.is_valid()

    def test_form_status_choices(self, circuit):
        """Test status field choices."""
        valid_statuses = ['open', 'in_progress', 'pending', 'resolved', 'closed']

        for status_choice in valid_statuses:
            form_data = {
                'circuit': circuit.pk,
                'ticket_number': f'TKT-{status_choice}',
                'subject': 'Test',
                'description': 'Test',
                'status': status_choice
            }
            form = CircuitTicketForm(data=form_data)
            assert form.is_valid()

    def test_form_priority_choices(self, circuit):
        """Test priority field choices."""
        valid_priorities = ['low', 'medium', 'high', 'critical']

        for priority_choice in valid_priorities:
            form_data = {
                'circuit': circuit.pk,
                'ticket_number': f'TKT-{priority_choice}',
                'subject': 'Test',
                'description': 'Test',
                'priority': priority_choice
            }
            form = CircuitTicketForm(data=form_data)
            assert form.is_valid()

    def test_form_url_validation(self, circuit):
        """Test external URL validation."""
        form_data = {
            'circuit': circuit.pk,
            'ticket_number': 'TKT-123',
            'subject': 'Test',
            'description': 'Test',
            'external_url': 'not-a-valid-url'
        }
        form = CircuitTicketForm(data=form_data)
        assert not form.is_valid()
        assert 'external_url' in form.errors


@pytest.mark.django_db
class TestCircuitPathForm:
    """Test CircuitPathForm validation."""

    def test_valid_circuit_path_form(self, circuit):
        """Test form with valid data."""
        form_data = {
            'circuit': circuit.pk,
            'map_center_lat': Decimal('37.7749'),
            'map_center_lon': Decimal('-122.4194'),
            'map_zoom': 10,
            'path_distance_km': Decimal('25.5')
        }
        form = CircuitPathForm(data=form_data)
        assert form.is_valid()

    def test_form_with_kmz_upload(self, circuit):
        """Test form with KMZ file upload."""
        file_content = b'KMZ content'
        uploaded_file = SimpleUploadedFile(
            'path.kmz',
            file_content,
            content_type='application/vnd.google-earth.kmz'
        )

        form_data = {
            'circuit': circuit.pk,
            'map_zoom': 10
        }
        form = CircuitPathForm(
            data=form_data,
            files={'kmz_file': uploaded_file}
        )
        assert form.is_valid()

    def test_form_coordinate_validation(self, circuit):
        """Test coordinate field validation."""
        # Test invalid latitude
        form_data = {
            'circuit': circuit.pk,
            'map_center_lat': 'invalid',
            'map_center_lon': Decimal('-122.4194'),
            'map_zoom': 10
        }
        form = CircuitPathForm(data=form_data)
        assert not form.is_valid()

    def test_form_optional_fields(self, circuit):
        """Test form with only required field."""
        form_data = {
            'circuit': circuit.pk,
            'map_zoom': 10
        }
        form = CircuitPathForm(data=form_data)
        assert form.is_valid()


@pytest.mark.django_db
class TestProviderAPIConfigForm:
    """Test ProviderAPIConfigForm validation."""

    def test_valid_provider_api_config_form(self, provider):
        """Test form with valid data."""
        form_data = {
            'provider': provider.pk,
            'provider_type': 'lumen',
            'api_endpoint': 'https://api.lumen.com',
            'api_key': 'test_key',
            'api_secret': 'test_secret',
            'sync_enabled': True,
            'sync_interval_hours': 24
        }
        form = ProviderAPIConfigForm(data=form_data)
        assert form.is_valid()

    def test_form_url_validation(self, provider):
        """Test API endpoint URL validation."""
        form_data = {
            'provider': provider.pk,
            'provider_type': 'lumen',
            'api_endpoint': 'not-a-valid-url',
            'sync_interval_hours': 24
        }
        form = ProviderAPIConfigForm(data=form_data)
        assert not form.is_valid()
        assert 'api_endpoint' in form.errors

    def test_form_provider_type_choices(self, provider):
        """Test provider type choices."""
        valid_types = ['lumen', 'att', 'verizon', 'zayo', 'custom']

        for provider_type in valid_types:
            form_data = {
                'provider': provider.pk,
                'provider_type': provider_type,
                'api_endpoint': 'https://api.example.com',
                'sync_interval_hours': 24
            }
            form = ProviderAPIConfigForm(data=form_data)
            assert form.is_valid()

    def test_form_password_field_rendering(self, provider):
        """Test that api_secret is rendered as password field."""
        form = ProviderAPIConfigForm()
        # Check that the widget is a password input
        assert form.fields['api_secret'].widget.input_type == 'password'
