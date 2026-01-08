# Provider API Integration Guide

This guide explains how to create custom provider integrations for syncing circuit data from carrier APIs.

## Overview

The Circuit Manager plugin includes an extensible framework for integrating with carrier/provider APIs. You can create custom integrations for any provider by extending the `BaseProviderSync` class.

## Architecture

```
BaseProviderSync (Abstract Base Class)
    ├── LumenProviderSync (Example Implementation)
    ├── ATTProviderSync (Your Implementation)
    └── CustomProviderSync (Your Implementation)
```

## Creating a Custom Provider Integration

### Step 1: Create Provider Class

Create a new Python file in the `providers/` directory:

```python
# netbox_circuit_manager/providers/mycarrier.py

from typing import Dict, List
from decimal import Decimal
from datetime import datetime
from .base import BaseProviderSync
from .registry import provider_registry
from ..models import CircuitCost


class MyCarrierProviderSync(BaseProviderSync):
    """
    Integration for MyCarrier API.
    """

    provider_name = 'mycarrier'

    def authenticate(self) -> bool:
        """
        Authenticate with the provider API.
        """
        try:
            # Implement your authentication logic
            response = self.session.post(
                f'{self.api_endpoint}/auth',
                json={
                    'username': self.api_key,
                    'password': self.api_secret
                }
            )

            if response.status_code == 200:
                token = response.json()['token']
                self.session.headers.update({
                    'Authorization': f'Bearer {token}'
                })
                return True

            return False

        except Exception as e:
            print(f"Authentication error: {e}")
            return False

    def get_circuits(self) -> List[Dict]:
        """
        Retrieve list of circuits from provider API.
        """
        try:
            response = self.session.get(
                f'{self.api_endpoint}/circuits'
            )
            response.raise_for_status()
            return response.json()['data']

        except Exception as e:
            print(f"Error fetching circuits: {e}")
            return []

    def get_circuit_details(self, circuit_id: str) -> Dict:
        """
        Get detailed information for a specific circuit.
        """
        try:
            response = self.session.get(
                f'{self.api_endpoint}/circuits/{circuit_id}'
            )
            response.raise_for_status()
            return response.json()

        except Exception as e:
            print(f"Error fetching circuit details: {e}")
            return {}

    def sync_circuit_costs(self, circuit, provider_data: Dict) -> bool:
        """
        Sync cost information from provider API.
        """
        try:
            # Extract cost data from provider response
            # Adapt this to your provider's data structure
            billing = provider_data.get('billing', {})

            nrc = billing.get('setup_fee')
            mrc = billing.get('monthly_fee')
            currency = billing.get('currency', 'USD')

            # Update or create CircuitCost
            cost, created = CircuitCost.objects.update_or_create(
                circuit=circuit,
                defaults={
                    'nrc': Decimal(str(nrc)) if nrc else None,
                    'mrc': Decimal(str(mrc)) if mrc else None,
                    'currency': currency,
                    'last_updated_date': datetime.now().date(),
                }
            )

            return True

        except Exception as e:
            print(f"Error syncing circuit costs: {e}")
            return False


# Register the provider
provider_registry.register('mycarrier', MyCarrierProviderSync)
```

### Step 2: Register the Provider

Add your provider to the `PROVIDER_CHOICES` in [models.py](netbox_circuit_manager/models.py:324):

```python
PROVIDER_CHOICES = (
    ('lumen', 'Lumen'),
    ('att', 'AT&T'),
    ('verizon', 'Verizon'),
    ('zayo', 'Zayo'),
    ('mycarrier', 'MyCarrier'),  # Add your provider
    ('custom', 'Custom'),
)
```

### Step 3: Import Your Provider

Add an import in `providers/__init__.py`:

```python
from .base import BaseProviderSync
from .registry import provider_registry
from .lumen import LumenProviderSync
from .mycarrier import MyCarrierProviderSync  # Import your provider

__all__ = ['BaseProviderSync', 'provider_registry']
```

## Required Methods

Your provider class MUST implement these methods:

### `authenticate() -> bool`
Authenticate with the provider API and set up session headers.

**Returns:** `True` if authentication successful

### `get_circuits() -> List[Dict]`
Retrieve a list of all circuits from the provider.

**Returns:** List of circuit dictionaries

### `get_circuit_details(circuit_id: str) -> Dict`
Get detailed information for a specific circuit.

**Parameters:**
- `circuit_id`: Provider's circuit identifier

**Returns:** Dictionary containing circuit details

### `sync_circuit_costs(circuit, provider_data: Dict) -> bool`
Sync cost information (NRC/MRC) for a circuit.

**Parameters:**
- `circuit`: NetBox Circuit instance
- `provider_data`: Data from provider API

**Returns:** `True` if sync successful

## Optional Methods

Override these methods if your provider supports them:

### `sync_circuit_tickets(circuit, provider_data: Dict) -> bool`
Sync ticket/trouble ticket information.

### `sync_circuit_path(circuit, provider_data: Dict) -> bool`
Sync geographic path/route information.

### `_match_circuit(provider_data: Dict) -> Optional[Circuit]`
Custom logic to match provider circuits to NetBox circuits.

Default behavior matches by Circuit ID (cid).

## Using the Provider

### Via Web Interface

1. Navigate to **Circuit Manager > Provider API Configs**
2. Click **Add**
3. Fill in the form:
   - **Provider**: Select the NetBox provider
   - **Provider Type**: Select your custom provider
   - **API Endpoint**: Enter the base URL
   - **API Key**: Your API key
   - **API Secret**: Your API secret
   - **Sync Enabled**: Check to enable automatic sync
   - **Sync Interval Hours**: How often to sync

### Via Management Command

Test connection:

```bash
python manage.py sync_provider --provider <config_id> --test
```

Run manual sync:

```bash
python manage.py sync_provider --provider <config_id>
```

Sync all enabled providers:

```bash
python manage.py sync_provider
```

## Example: AT&T Provider

Here's a complete example for AT&T:

```python
# providers/att.py

from typing import Dict, List
from decimal import Decimal
from .base import BaseProviderSync
from .registry import provider_registry
from ..models import CircuitCost


class ATTProviderSync(BaseProviderSync):
    provider_name = 'att'

    def authenticate(self) -> bool:
        try:
            # AT&T uses OAuth2
            response = self.session.post(
                f'{self.api_endpoint}/oauth/token',
                data={
                    'grant_type': 'client_credentials',
                    'client_id': self.api_key,
                    'client_secret': self.api_secret,
                }
            )

            if response.status_code == 200:
                token = response.json()['access_token']
                self.session.headers.update({
                    'Authorization': f'Bearer {token}'
                })
                return True

            return False

        except Exception as e:
            print(f"AT&T authentication error: {e}")
            return False

    def get_circuits(self) -> List[Dict]:
        try:
            response = self.session.get(
                f'{self.api_endpoint}/v2/circuits',
                params={'status': 'active'}
            )
            response.raise_for_status()
            return response.json()['circuits']

        except Exception as e:
            print(f"Error fetching AT&T circuits: {e}")
            return []

    def get_circuit_details(self, circuit_id: str) -> Dict:
        try:
            response = self.session.get(
                f'{self.api_endpoint}/v2/circuits/{circuit_id}',
                params={'include': 'billing,tickets'}
            )
            response.raise_for_status()
            return response.json()

        except Exception as e:
            print(f"Error fetching AT&T circuit details: {e}")
            return {}

    def sync_circuit_costs(self, circuit, provider_data: Dict) -> bool:
        try:
            billing = provider_data.get('billing_info', {})

            cost, created = CircuitCost.objects.update_or_create(
                circuit=circuit,
                defaults={
                    'nrc': Decimal(str(billing.get('installation_charge', 0))),
                    'mrc': Decimal(str(billing.get('monthly_charge', 0))),
                    'currency': 'USD',
                    'billing_account': billing.get('ban', ''),
                }
            )

            return True

        except Exception as e:
            print(f"Error syncing AT&T costs: {e}")
            return False


provider_registry.register('att', ATTProviderSync)
```

## Testing Your Integration

### 1. Unit Tests

Create tests in `tests/test_providers.py`:

```python
from django.test import TestCase
from netbox_circuit_manager.providers.mycarrier import MyCarrierProviderSync
from netbox_circuit_manager.models import ProviderAPIConfig


class MyCarrierProviderSyncTest(TestCase):
    def setUp(self):
        # Create test API config
        self.config = ProviderAPIConfig.objects.create(
            provider_type='mycarrier',
            api_endpoint='https://api.mycarrier.com',
            api_key='test_key',
            api_secret='test_secret',
        )

    def test_authentication(self):
        sync = MyCarrierProviderSync(self.config)
        # Mock the API response and test
        pass
```

### 2. Manual Testing

```bash
# Test connection
python manage.py sync_provider --provider 1 --test

# Test sync
python manage.py sync_provider --provider 1
```

## Common Patterns

### Pagination

```python
def get_circuits(self) -> List[Dict]:
    all_circuits = []
    page = 1

    while True:
        response = self.session.get(
            f'{self.api_endpoint}/circuits',
            params={'page': page, 'per_page': 100}
        )
        data = response.json()
        all_circuits.extend(data['circuits'])

        if not data.get('has_more'):
            break

        page += 1

    return all_circuits
```

### Rate Limiting

```python
import time

def get_circuit_details(self, circuit_id: str) -> Dict:
    # Add delay to respect rate limits
    time.sleep(0.5)

    response = self.session.get(
        f'{self.api_endpoint}/circuits/{circuit_id}'
    )
    return response.json()
```

### Error Handling

```python
def sync_circuit_costs(self, circuit, provider_data: Dict) -> bool:
    try:
        billing = provider_data.get('billing')
        if not billing:
            print(f"No billing data for circuit {circuit.cid}")
            return False

        # ... sync logic ...

        return True

    except KeyError as e:
        print(f"Missing required field: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False
```

## Security Considerations

1. **API Credentials**: Store API secrets securely. Consider encrypting them in the database.
2. **HTTPS**: Always use HTTPS for API endpoints.
3. **Timeouts**: Set reasonable timeouts for API requests.
4. **Logging**: Don't log sensitive information (API keys, secrets).

## Support

For questions or issues with provider integrations:
- Check the example implementations in `providers/lumen.py`
- Review the base class documentation in `providers/base.py`
- Open an issue on GitHub
