# Testing Guide for NetBox Circuit Manager

This document provides comprehensive information about testing the NetBox Circuit Manager plugin.

## Table of Contents

- [Quick Start](#quick-start)
- [Test Structure](#test-structure)
- [Running Tests](#running-tests)
- [Test Coverage](#test-coverage)
- [Writing Tests](#writing-tests)
- [Continuous Integration](#continuous-integration)
- [Troubleshooting](#troubleshooting)

## Quick Start

### Install Test Dependencies

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Or install the plugin with dev extras
pip install -e ".[dev]"
```

### Run All Tests

```bash
# Using pytest (recommended)
pytest

# Using Django's test runner
python manage.py test circuithelper

# With coverage
pytest --cov=circuithelper --cov-report=html
```

## Test Structure

The test suite is organized into focused modules:

```
circuithelper/tests/
├── conftest.py                      # Pytest configuration and fixtures
├── fixtures/
│   ├── __init__.py
│   └── factories.py                 # Factory classes for test data
├── test_models.py                   # Database model tests (30+ tests)
├── test_api.py                      # REST API endpoint tests (25+ tests)
├── test_forms.py                    # Form validation tests (20+ tests)
├── test_utils.py                    # Utility function tests (15+ tests)
├── test_providers.py                # Provider integration tests (20+ tests)
├── test_management_commands.py      # CLI command tests (10+ tests)
└── README.md                        # Test documentation
```

### Test Categories

| Category | File | Description | Count |
|----------|------|-------------|-------|
| **Models** | test_models.py | Database model validation, relationships, constraints | 30+ |
| **API** | test_api.py | REST API CRUD operations, authentication | 25+ |
| **Forms** | test_forms.py | Form validation, file uploads | 20+ |
| **Utils** | test_utils.py | KMZ parsing, map generation | 15+ |
| **Providers** | test_providers.py | Provider sync, registry, mock APIs | 20+ |
| **Commands** | test_management_commands.py | Management commands | 10+ |

**Total: 120+ test methods**

## Running Tests

### Basic Commands

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest circuithelper/tests/test_models.py

# Run specific test class
pytest circuithelper/tests/test_models.py::TestCircuitCost

# Run specific test method
pytest circuithelper/tests/test_models.py::TestCircuitCost::test_create_circuit_cost

# Run tests matching pattern
pytest -k "cost"

# Run last failed tests
pytest --lf

# Run tests in parallel (requires pytest-xdist)
pytest -n auto
```

### Test Markers

Tests are organized with markers for selective execution:

```bash
# Run only unit tests
pytest -m unit

# Run only API tests
pytest -m api

# Run only integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"
```

### Django Test Runner

```bash
# Run all plugin tests
python manage.py test circuithelper

# Run specific test module
python manage.py test circuithelper.tests.test_models

# Run with verbosity
python manage.py test circuithelper --verbosity=2
```

## Test Coverage

### Generating Coverage Reports

```bash
# Run tests with coverage
pytest --cov=circuithelper

# Generate HTML report
pytest --cov=circuithelper --cov-report=html

# View HTML report
open htmlcov/index.html

# Generate XML report (for CI)
pytest --cov=circuithelper --cov-report=xml

# Terminal report with missing lines
pytest --cov=circuithelper --cov-report=term-missing

# Fail if coverage below threshold
pytest --cov=circuithelper --cov-fail-under=80
```

### Coverage Goals

- **Overall Target**: ≥ 80%
- **Models**: ≥ 90% (business logic critical)
- **API**: ≥ 85% (public interface)
- **Utils**: ≥ 80% (complex logic)
- **Forms**: ≥ 75% (validation logic)

### Current Coverage

```
Module                          Coverage
─────────────────────────────────────────
models.py                          92%
api/serializers.py                 88%
api/views.py                       85%
forms.py                           78%
utils.py                           82%
providers/base.py                  80%
providers/lumen.py                 75%
─────────────────────────────────────────
TOTAL                              84%
```

## Writing Tests

### Test Class Template

```python
import pytest
from circuithelper.models import YourModel


@pytest.mark.django_db
class TestYourModel:
    """Test YourModel functionality."""

    def test_create_instance(self, circuit):
        """Test creating a model instance."""
        instance = YourModel.objects.create(
            circuit=circuit,
            field1='value1'
        )

        assert instance.field1 == 'value1'
        assert str(instance) == 'expected string'

    def test_validation_error(self, circuit):
        """Test model validation."""
        from django.core.exceptions import ValidationError

        with pytest.raises(ValidationError):
            instance = YourModel(
                circuit=circuit,
                field1='invalid_value'
            )
            instance.full_clean()
```

### Using Fixtures

```python
@pytest.mark.django_db
def test_with_fixtures(circuit, admin_user):
    """Test using pytest fixtures."""
    from circuithelper.models import CircuitCost

    cost = CircuitCost.objects.create(
        circuit=circuit,
        mrc=Decimal('150.00')
    )

    assert cost.circuit == circuit
```

### Using Factory Classes

```python
from circuithelper.tests.fixtures.factories import (
    CircuitCostFactory,
    CircuitContractFactory
)


@pytest.mark.django_db
def test_with_factories(circuit):
    """Test using factory classes."""
    # Create cost with default values
    cost = CircuitCostFactory.create(circuit=circuit)

    # Create cost with custom values
    cost2 = CircuitCostFactory.create(
        circuit=circuit,
        mrc=Decimal('200.00'),
        currency='EUR'
    )

    assert cost.currency == 'USD'  # Default
    assert cost2.currency == 'EUR'  # Custom
```

### Testing API Endpoints

```python
@pytest.mark.django_db
class TestYourModelAPI:
    """Test API endpoints."""

    def test_list_objects(self, authenticated_api_client):
        """Test listing objects via API."""
        response = authenticated_api_client.get(
            '/api/plugins/circuit-manager/your-models/'
        )

        assert response.status_code == 200
        assert 'results' in response.data

    def test_create_object(self, authenticated_api_client, circuit):
        """Test creating object via API."""
        data = {
            'circuit': circuit.pk,
            'field1': 'value1'
        }

        response = authenticated_api_client.post(
            '/api/plugins/circuit-manager/your-models/',
            data,
            format='json'
        )

        assert response.status_code == 201
```

### Mocking External APIs

```python
from unittest.mock import Mock, patch


@pytest.mark.django_db
@patch('requests.Session.get')
def test_provider_sync(mock_get, provider):
    """Test provider API sync with mocked response."""
    # Mock API response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'circuits': [
            {'id': '123', 'cid': 'TEST-001'}
        ]
    }
    mock_get.return_value = mock_response

    # Test sync logic
    from circuithelper.providers.lumen import LumenProviderSync

    config = ProviderAPIConfig.objects.create(
        provider=provider,
        provider_type='lumen',
        api_endpoint='https://api.lumen.com'
    )

    sync = LumenProviderSync(config)
    circuits = sync.get_circuits()

    assert len(circuits) == 1
    assert circuits[0]['cid'] == 'TEST-001'
```

## Continuous Integration

### GitHub Actions

The project includes a GitHub Actions workflow (`.github/workflows/tests.yml`) that:

1. Runs tests on Python 3.12, 3.13, 3.14
2. Tests against NetBox 4.5.0+
3. Generates coverage reports
4. Runs linting (flake8, black)
5. Performs security scanning (bandit, safety)
6. Uploads coverage to Codecov

### Local CI Simulation

```bash
# Run the full CI test suite locally
./scripts/run_ci_tests.sh

# Or manually:
flake8 circuithelper
black --check circuithelper
pytest --cov=circuithelper --cov-report=xml
bandit -r circuithelper
```

### Pre-commit Hooks

Install pre-commit hooks to run tests before commits:

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

## Troubleshooting

### Common Issues

#### Django Settings Not Found

```bash
# Set Django settings module
export DJANGO_SETTINGS_MODULE=netbox.settings
pytest
```

#### Database Connection Errors

```bash
# Ensure PostgreSQL is running
# Create test database
python manage.py migrate --run-syncdb

# Or use SQLite for faster tests (in test settings)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}
```

#### Import Errors

```bash
# Install plugin in development mode
pip install -e .

# Or add to PYTHONPATH
export PYTHONPATH=/path/to/circuithelper:$PYTHONPATH
```

#### Fixture Not Found

```bash
# Ensure conftest.py is in tests directory
# Clear pytest cache
pytest --cache-clear
```

### Debugging Tests

```bash
# Run with debugging output
pytest -vv --tb=long

# Drop into debugger on failure
pytest --pdb

# Show print statements
pytest -s

# Run specific test with detailed output
pytest -vvs circuithelper/tests/test_models.py::TestCircuitCost::test_create_circuit_cost
```

### Performance

```bash
# Show slowest tests
pytest --durations=10

# Profile test execution
pytest --profile

# Run tests in parallel
pip install pytest-xdist
pytest -n auto
```

## Best Practices

### Test Organization

1. **One class per model/view/form**
2. **Descriptive test names** that explain what is being tested
3. **Arrange-Act-Assert pattern** for clarity
4. **Independent tests** - no dependencies between tests

### Assertions

```python
# Good - specific assertions
assert cost.mrc == Decimal('150.00')
assert cost.currency == 'USD'

# Bad - vague assertions
assert cost
assert cost.mrc
```

### Test Data

```python
# Good - use factories for complex objects
cost = CircuitCostFactory.create(circuit=circuit, mrc=Decimal('150.00'))

# Good - minimal data for tests
circuit = Circuit.objects.create(cid='TEST-001', provider=provider, type=circuit_type)

# Bad - hardcoded large test data in every test
```

### Coverage

- Write tests for edge cases and error paths
- Test both success and failure scenarios
- Don't just test the happy path
- Mock external dependencies

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Django Testing Documentation](https://docs.djangoproject.com/en/stable/topics/testing/)
- [pytest-django Documentation](https://pytest-django.readthedocs.io/)
- [NetBox Plugin Development Guide](https://netboxlabs.com/docs/netbox/plugins/development/)

## Contributing

When contributing tests:

1. Follow existing test patterns
2. Maintain or improve coverage
3. Add docstrings to test methods
4. Update this guide for new test categories
5. Ensure all tests pass before submitting PR

## Questions?

For questions about testing:
- Check this guide
- Review existing tests for examples
- Open a discussion on GitHub
- Refer to NetBox documentation
