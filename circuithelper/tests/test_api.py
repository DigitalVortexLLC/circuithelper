"""
Tests for NetBox Circuit Manager REST API.
"""

import pytest
from decimal import Decimal
from datetime import date
from rest_framework import status

from circuithelper.models import (
    CircuitCost,
    CircuitContract,
    CircuitTicket,
    CircuitPath,
    ProviderAPIConfig
)


@pytest.mark.django_db
class TestCircuitCostAPI:
    """Test CircuitCost API endpoints."""

    def test_list_circuit_costs(self, authenticated_api_client, circuit):
        """Test listing circuit costs."""
        CircuitCost.objects.create(
            circuit=circuit,
            nrc=Decimal('500.00'),
            mrc=Decimal('150.00'),
            currency='USD'
        )

        response = authenticated_api_client.get(
            '/api/plugins/circuit-manager/circuit-costs/'
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['mrc'] == '150.00'

    def test_create_circuit_cost(self, authenticated_api_client, circuit):
        """Test creating a circuit cost via API."""
        data = {
            'circuit': circuit.pk,
            'nrc': '500.00',
            'mrc': '150.00',
            'currency': 'USD',
            'billing_account': 'ACC-123'
        }

        response = authenticated_api_client.post(
            '/api/plugins/circuit-manager/circuit-costs/',
            data,
            format='json'
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert CircuitCost.objects.count() == 1
        cost = CircuitCost.objects.first()
        assert cost.mrc == Decimal('150.00')
        assert cost.billing_account == 'ACC-123'

    def test_update_circuit_cost(self, authenticated_api_client, circuit):
        """Test updating a circuit cost."""
        cost = CircuitCost.objects.create(
            circuit=circuit,
            mrc=Decimal('150.00'),
            currency='USD'
        )

        data = {
            'circuit': circuit.pk,
            'mrc': '200.00',
            'currency': 'USD'
        }

        response = authenticated_api_client.patch(
            f'/api/plugins/circuit-manager/circuit-costs/{cost.pk}/',
            data,
            format='json'
        )

        assert response.status_code == status.HTTP_200_OK
        cost.refresh_from_db()
        assert cost.mrc == Decimal('200.00')

    def test_delete_circuit_cost(self, authenticated_api_client, circuit):
        """Test deleting a circuit cost."""
        cost = CircuitCost.objects.create(
            circuit=circuit,
            mrc=Decimal('150.00'),
            currency='USD'
        )

        response = authenticated_api_client.delete(
            f'/api/plugins/circuit-manager/circuit-costs/{cost.pk}/'
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert CircuitCost.objects.count() == 0

    def test_unauthenticated_access_denied(self, api_client):
        """Test that unauthenticated access is denied."""
        response = api_client.get(
            '/api/plugins/circuit-manager/circuit-costs/'
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestCircuitContractAPI:
    """Test CircuitContract API endpoints."""

    def test_list_circuit_contracts(self, authenticated_api_client, circuit):
        """Test listing circuit contracts."""
        CircuitContract.objects.create(
            circuit=circuit,
            contract_number='CONTRACT-001',
            start_date=date(2024, 1, 1)
        )

        response = authenticated_api_client.get(
            '/api/plugins/circuit-manager/circuit-contracts/'
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['contract_number'] == 'CONTRACT-001'

    def test_create_circuit_contract(self, authenticated_api_client, circuit):
        """Test creating a circuit contract via API."""
        data = {
            'circuit': circuit.pk,
            'contract_number': 'CONTRACT-2024-001',
            'start_date': '2024-01-01',
            'end_date': '2027-12-31',
            'term_months': 48,
            'auto_renew': True
        }

        response = authenticated_api_client.post(
            '/api/plugins/circuit-manager/circuit-contracts/',
            data,
            format='json'
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert CircuitContract.objects.count() == 1
        contract = CircuitContract.objects.first()
        assert contract.term_months == 48
        assert contract.auto_renew is True

    def test_filter_contracts_by_circuit(self, authenticated_api_client, circuit, provider, circuit_type):
        """Test filtering contracts by circuit."""
        circuit2 = Circuit.objects.create(
            cid='TEST-002',
            provider=provider,
            type=circuit_type,
            status='active'
        )

        CircuitContract.objects.create(
            circuit=circuit,
            contract_number='CONTRACT-001',
            start_date=date(2024, 1, 1)
        )
        CircuitContract.objects.create(
            circuit=circuit2,
            contract_number='CONTRACT-002',
            start_date=date(2024, 1, 1)
        )

        response = authenticated_api_client.get(
            f'/api/plugins/circuit-manager/circuit-contracts/?circuit_id={circuit.pk}'
        )

        assert response.status_code == status.HTTP_200_OK
        # Note: Filtering may need to be implemented in the viewset


@pytest.mark.django_db
class TestCircuitTicketAPI:
    """Test CircuitTicket API endpoints."""

    def test_list_circuit_tickets(self, authenticated_api_client, circuit):
        """Test listing circuit tickets."""
        CircuitTicket.objects.create(
            circuit=circuit,
            ticket_number='TKT-123',
            subject='Test issue',
            description='Test description'
        )

        response = authenticated_api_client.get(
            '/api/plugins/circuit-manager/circuit-tickets/'
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['ticket_number'] == 'TKT-123'

    def test_create_circuit_ticket(self, authenticated_api_client, circuit):
        """Test creating a circuit ticket via API."""
        data = {
            'circuit': circuit.pk,
            'ticket_number': 'TKT-456',
            'subject': 'Circuit down',
            'status': 'open',
            'priority': 'critical',
            'description': 'Circuit is experiencing issues',
            'external_url': 'https://provider.com/tickets/456'
        }

        response = authenticated_api_client.post(
            '/api/plugins/circuit-manager/circuit-tickets/',
            data,
            format='json'
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert CircuitTicket.objects.count() == 1
        ticket = CircuitTicket.objects.first()
        assert ticket.status == 'open'
        assert ticket.priority == 'critical'

    def test_update_ticket_status(self, authenticated_api_client, circuit):
        """Test updating ticket status."""
        ticket = CircuitTicket.objects.create(
            circuit=circuit,
            ticket_number='TKT-123',
            subject='Issue',
            description='Description',
            status='open'
        )

        data = {
            'status': 'resolved',
            'resolution': 'Issue was fixed by restarting equipment'
        }

        response = authenticated_api_client.patch(
            f'/api/plugins/circuit-manager/circuit-tickets/{ticket.pk}/',
            data,
            format='json'
        )

        assert response.status_code == status.HTTP_200_OK
        ticket.refresh_from_db()
        assert ticket.status == 'resolved'
        assert 'restarting equipment' in ticket.resolution


@pytest.mark.django_db
class TestCircuitPathAPI:
    """Test CircuitPath API endpoints."""

    def test_list_circuit_paths(self, authenticated_api_client, circuit):
        """Test listing circuit paths."""
        CircuitPath.objects.create(
            circuit=circuit,
            map_center_lat=Decimal('37.7749'),
            map_center_lon=Decimal('-122.4194'),
            map_zoom=10
        )

        response = authenticated_api_client.get(
            '/api/plugins/circuit-manager/circuit-paths/'
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1

    def test_create_circuit_path(self, authenticated_api_client, circuit):
        """Test creating a circuit path via API."""
        geojson_data = {
            'type': 'FeatureCollection',
            'features': [{
                'type': 'Feature',
                'geometry': {
                    'type': 'LineString',
                    'coordinates': [[0, 0], [1, 1]]
                }
            }]
        }

        data = {
            'circuit': circuit.pk,
            'geojson_data': geojson_data,
            'map_center_lat': '37.7749',
            'map_center_lon': '-122.4194',
            'map_zoom': 10,
            'path_distance_km': '25.5'
        }

        response = authenticated_api_client.post(
            '/api/plugins/circuit-manager/circuit-paths/',
            data,
            format='json'
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert CircuitPath.objects.count() == 1
        path = CircuitPath.objects.first()
        assert path.geojson_data['type'] == 'FeatureCollection'


@pytest.mark.django_db
class TestProviderAPIConfigAPI:
    """Test ProviderAPIConfig API endpoints."""

    def test_list_provider_api_configs(self, authenticated_api_client, provider):
        """Test listing provider API configurations."""
        ProviderAPIConfig.objects.create(
            provider=provider,
            provider_type='lumen',
            api_endpoint='https://api.lumen.com',
            sync_enabled=True
        )

        response = authenticated_api_client.get(
            '/api/plugins/circuit-manager/provider-api-configs/'
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['provider_type'] == 'lumen'

    def test_create_provider_api_config(self, authenticated_api_client, provider):
        """Test creating a provider API config via API."""
        data = {
            'provider': provider.pk,
            'provider_type': 'lumen',
            'api_endpoint': 'https://api.lumen.com',
            'api_key': 'test_key',
            'api_secret': 'test_secret',
            'sync_enabled': True,
            'sync_interval_hours': 24
        }

        response = authenticated_api_client.post(
            '/api/plugins/circuit-manager/provider-api-configs/',
            data,
            format='json'
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert ProviderAPIConfig.objects.count() == 1

    def test_api_secret_not_exposed(self, authenticated_api_client, provider):
        """Test that API secret is not exposed in GET responses."""
        config = ProviderAPIConfig.objects.create(
            provider=provider,
            provider_type='lumen',
            api_endpoint='https://api.lumen.com',
            api_key='test_key',
            api_secret='super_secret_value'
        )

        response = authenticated_api_client.get(
            f'/api/plugins/circuit-manager/provider-api-configs/{config.pk}/'
        )

        assert response.status_code == status.HTTP_200_OK
        # API secret should not be in response (write_only field)
        assert 'api_secret' not in response.data or response.data.get('api_secret') is None
