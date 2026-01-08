# NetBox Circuit Manager Tests

Comprehensive test suite for the NetBox Circuit Manager plugin.

## Test Structure

```
tests/
├── conftest.py                      # Pytest fixtures and configuration
├── fixtures/
│   ├── factories.py                 # Factory classes for test data
│   └── __init__.py
├── test_models.py                   # Model tests
├── test_api.py                      # REST API tests
├── test_forms.py                    # Form validation tests
├── test_utils.py                    # Utility function tests
├── test_providers.py                # Provider integration tests
├── test_management_commands.py      # Management command tests
└── README.md                        # This file
```

## Running Tests

### All Tests

```bash
# Using pytest
pytest

# Using Django's test runner
python manage.py test netbox_circuit_manager
```

### Specific Test Files

```bash
# Test models only
pytest netbox_circuit_manager/tests/test_models.py

# Test API only
pytest netbox_circuit_manager/tests/test_api.py

# Test a specific test class
pytest netbox_circuit_manager/tests/test_models.py::TestCircuitCost

# Test a specific test method
pytest netbox_circuit_manager/tests/test_models.py::TestCircuitCost::test_create_circuit_cost
```

### With Coverage

```bash
# Generate coverage report
pytest --cov=netbox_circuit_manager --cov-report=html

# View coverage report
open htmlcov/index.html
```

### With Markers

```bash
# Run only unit tests
pytest -m unit

# Run only API tests
pytest -m api

# Skip slow tests
pytest -m "not slow"
```

## Test Categories

### Model Tests (`test_models.py`)

Tests for all database models:
- CircuitCost - Financial tracking
- CircuitContract - Contract management
- CircuitTicket - Ticket integration
- CircuitPath - Geographic path data
- ProviderAPIConfig - Provider API configurations

**Coverage:**
- Model creation and validation
- Field constraints and defaults
- Relationships (OneToOne, ForeignKey)
- String representations
- Unique constraints
- File uploads

### API Tests (`test_api.py`)

Tests for REST API endpoints:
- List, create, update, delete operations
- Authentication and permissions
- Serialization and deserialization
- Filtering and pagination
- Field visibility (e.g., api_secret write-only)

**Coverage:**
- All CRUD operations for each model
- Nested serializers
- API authentication
- Error handling

### Form Tests (`test_forms.py`)

Tests for Django forms:
- Form validation
- Required vs optional fields
- Field type validation
- File upload handling
- Choice field options

**Coverage:**
- CircuitCostForm
- CircuitContractForm
- CircuitTicketForm
- CircuitPathForm
- ProviderAPIConfigForm

### Utility Tests (`test_utils.py`)

Tests for utility functions:
- KMZ file parsing
- KML to GeoJSON conversion
- Coordinate extraction
- Path distance calculation
- Folium map generation

**Coverage:**
- Valid and invalid file formats
- Edge cases (empty files, malformed data)
- Geographic calculations
- Map HTML generation

### Provider Tests (`test_providers.py`)

Tests for provider integration framework:
- Provider registry functionality
- Base provider sync class
- Lumen provider integration
- Authentication mechanisms
- Circuit matching logic
- Sync operations

**Coverage:**
- Provider registration/unregistration
- Mock provider implementations
- API mocking with unittest.mock
- Status and priority mapping

### Management Command Tests (`test_management_commands.py`)

Tests for Django management commands:
- sync_provider command
- Command-line arguments
- Output formatting
- Error handling

**Coverage:**
- Test mode (--test flag)
- Sync specific provider
- Sync all providers
- Disabled providers
- Connection failures

## Fixtures

### Pytest Fixtures (conftest.py)

Available fixtures for all tests:

- `test_user` - Regular user
- `admin_user` - Superuser
- `provider` - Test provider
- `circuit_type` - Test circuit type
- `circuit` - Test circuit
- `tenant` - Test tenant
- `api_client` - Unauthenticated API client
- `authenticated_api_client` - Authenticated API client

### Factory Classes (fixtures/factories.py)

Factory classes for creating test data:

```python
# Example usage
from netbox_circuit_manager.tests.fixtures.factories import (
    CircuitCostFactory,
    CircuitContractFactory,
    CircuitTicketFactory,
    CircuitPathFactory,
    ProviderAPIConfigFactory
)

# Create test data
cost = CircuitCostFactory.create(circuit=circuit, mrc=Decimal('200.00'))
contract = CircuitContractFactory.create(circuit=circuit)
ticket = CircuitTicketFactory.create(circuit=circuit, priority='critical')
```

## Writing New Tests

### Test Class Template

```python
import pytest
from netbox_circuit_manager.models import YourModel


@pytest.mark.django_db
class TestYourModel:
    """Test YourModel functionality."""

    def test_create_model(self, circuit):
        """Test creating a model instance."""
        instance = YourModel.objects.create(
            circuit=circuit,
            field1='value1'
        )

        assert instance.field1 == 'value1'
        assert str(instance) == 'expected string'

    def test_validation(self, circuit):
        """Test model validation."""
        with pytest.raises(ValidationError):
            instance = YourModel(
                circuit=circuit,
                field1='invalid'
            )
            instance.full_clean()
```

### API Test Template

```python
@pytest.mark.django_db
class TestYourModelAPI:
    """Test YourModel API endpoints."""

    def test_list_objects(self, authenticated_api_client):
        """Test listing objects."""
        response = authenticated_api_client.get(
            '/api/plugins/circuit-manager/your-models/'
        )

        assert response.status_code == 200
        assert len(response.data['results']) >= 0
```

## Best Practices

1. **Use Fixtures**: Leverage pytest fixtures for common test data
2. **Factory Classes**: Use factories for complex object creation
3. **Isolation**: Each test should be independent
4. **Descriptive Names**: Test names should describe what they test
5. **Assertions**: Use clear, specific assertions
6. **Mock External APIs**: Use `unittest.mock` for external API calls
7. **Coverage**: Aim for >80% code coverage

## Continuous Integration

Tests should run in CI/CD pipeline:

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: |
    pytest --cov=netbox_circuit_manager --cov-report=xml

- name: Upload coverage
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
```

## Troubleshooting

### Django Settings Not Found

```bash
# Set Django settings module
export DJANGO_SETTINGS_MODULE=netbox.settings
pytest
```

### Database Errors

```bash
# Create test database
python manage.py migrate --run-syncdb
pytest
```

### Import Errors

```bash
# Install plugin in development mode
pip install -e .
pytest
```

## Test Metrics

Current test coverage:

- **Model Tests**: 5 test classes, 30+ test methods
- **API Tests**: 5 test classes, 25+ test methods
- **Form Tests**: 5 test classes, 20+ test methods
- **Utility Tests**: 3 test classes, 15+ test methods
- **Provider Tests**: 3 test classes, 20+ test methods
- **Command Tests**: 2 test classes, 10+ test methods

**Total**: ~120+ test methods covering all major functionality

## Contributing

When adding new features:

1. Write tests first (TDD approach)
2. Ensure all tests pass
3. Maintain or improve coverage percentage
4. Document complex test scenarios
5. Update this README if adding new test categories
