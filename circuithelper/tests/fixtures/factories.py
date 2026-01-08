"""
Factory classes for creating test data.

These factories use factory_boy pattern for easier test data creation.
"""

from decimal import Decimal
from datetime import date, timedelta


class CircuitCostFactory:
    """Factory for creating CircuitCost instances."""

    @staticmethod
    def create(circuit, **kwargs):
        """Create a CircuitCost instance."""
        from circuithelper.models import CircuitCost

        defaults = {
            "nrc": Decimal("500.00"),
            "mrc": Decimal("150.00"),
            "currency": "USD",
            "billing_account": "ACC-123456",
        }
        defaults.update(kwargs)

        return CircuitCost.objects.create(circuit=circuit, **defaults)


class CircuitContractFactory:
    """Factory for creating CircuitContract instances."""

    @staticmethod
    def create(circuit, **kwargs):
        """Create a CircuitContract instance."""
        from circuithelper.models import CircuitContract

        defaults = {
            "contract_number": "CONTRACT-2024-001",
            "start_date": date.today(),
            "end_date": date.today() + timedelta(days=365 * 3),
            "term_months": 36,
            "auto_renew": True,
            "renewal_notice_days": 90,
        }
        defaults.update(kwargs)

        return CircuitContract.objects.create(circuit=circuit, **defaults)


class CircuitTicketFactory:
    """Factory for creating CircuitTicket instances."""

    @staticmethod
    def create(circuit, **kwargs):
        """Create a CircuitTicket instance."""
        from circuithelper.models import CircuitTicket

        defaults = {
            "ticket_number": "TKT-123456",
            "subject": "Circuit issue",
            "status": "open",
            "priority": "medium",
            "description": "Test ticket description",
        }
        defaults.update(kwargs)

        return CircuitTicket.objects.create(circuit=circuit, **defaults)


class CircuitPathFactory:
    """Factory for creating CircuitPath instances."""

    @staticmethod
    def create(circuit, **kwargs):
        """Create a CircuitPath instance."""
        from circuithelper.models import CircuitPath

        defaults = {
            "map_center_lat": Decimal("37.7749"),
            "map_center_lon": Decimal("-122.4194"),
            "map_zoom": 10,
            "path_distance_km": Decimal("25.5"),
            "geojson_data": {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "geometry": {
                            "type": "LineString",
                            "coordinates": [[-122.4194, 37.7749], [-122.4084, 37.7849]],
                        },
                        "properties": {"name": "Test Path"},
                    }
                ],
            },
        }
        defaults.update(kwargs)

        return CircuitPath.objects.create(circuit=circuit, **defaults)


class ProviderAPIConfigFactory:
    """Factory for creating ProviderAPIConfig instances."""

    @staticmethod
    def create(provider, **kwargs):
        """Create a ProviderAPIConfig instance."""
        from circuithelper.models import ProviderAPIConfig

        defaults = {
            "provider_type": "lumen",
            "api_endpoint": "https://api.lumen.com",
            "api_key": "test_api_key",
            "api_secret": "test_api_secret",
            "sync_enabled": True,
            "sync_interval_hours": 24,
        }
        defaults.update(kwargs)

        return ProviderAPIConfig.objects.create(provider=provider, **defaults)


class CircuitFactory:
    """Factory for creating Circuit instances."""

    @staticmethod
    def create(provider, circuit_type, **kwargs):
        """Create a Circuit instance."""
        from circuits.models import Circuit
        import random

        defaults = {"cid": f"TEST-CIRCUIT-{random.randint(1000, 9999)}", "status": "active"}
        defaults.update(kwargs)

        return Circuit.objects.create(provider=provider, type=circuit_type, **defaults)


class ProviderFactory:
    """Factory for creating Provider instances."""

    @staticmethod
    def create(**kwargs):
        """Create a Provider instance."""
        from circuits.models import Provider
        import random

        defaults = {
            "name": f"Test Provider {random.randint(1, 999)}",
            "slug": f"test-provider-{random.randint(1, 999)}",
        }
        defaults.update(kwargs)

        return Provider.objects.create(**defaults)


class CircuitTypeFactory:
    """Factory for creating CircuitType instances."""

    @staticmethod
    def create(**kwargs):
        """Create a CircuitType instance."""
        from circuits.models import CircuitType
        import random

        defaults = {
            "name": f"Circuit Type {random.randint(1, 999)}",
            "slug": f"circuit-type-{random.randint(1, 999)}",
        }
        defaults.update(kwargs)

        return CircuitType.objects.create(**defaults)
