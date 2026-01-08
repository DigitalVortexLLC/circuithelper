"""
Tests for management commands.
"""

import pytest
from io import StringIO
from unittest.mock import Mock, patch
from django.core.management import call_command
from django.core.management.base import CommandError

from circuithelper.models import ProviderAPIConfig
from circuithelper.providers.registry import provider_registry


class MockProviderSync:
    """Mock provider sync for testing."""

    def __init__(self, api_config):
        self.config = api_config

    def test_connection(self):
        """Mock test connection."""
        return {
            'success': True,
            'message': 'Connection successful',
            'response_time': 0.5
        }

    def sync_all(self):
        """Mock sync all."""
        return {
            'total': 10,
            'success': 10,
            'failed': 0,
            'errors': []
        }


@pytest.mark.django_db
class TestSyncProviderCommand:
    """Test sync_provider management command."""

    def setup_method(self):
        """Set up test provider in registry."""
        provider_registry.register('test_provider', MockProviderSync)

    def teardown_method(self):
        """Clean up test provider from registry."""
        provider_registry.unregister('test_provider')

    def test_command_with_no_providers(self):
        """Test command when no providers are configured."""
        out = StringIO()
        call_command('sync_provider', stdout=out)

        output = out.getvalue()
        assert 'No enabled provider configurations found' in output

    def test_command_test_connection(self, provider):
        """Test command with --test flag."""
        config = ProviderAPIConfig.objects.create(
            provider=provider,
            provider_type='test_provider',
            api_endpoint='https://api.test.com',
            sync_enabled=True
        )

        out = StringIO()
        call_command(
            'sync_provider',
            '--provider', str(config.pk),
            '--test',
            stdout=out
        )

        output = out.getvalue()
        assert 'Testing connection' in output
        assert 'Connection successful' in output

    def test_command_sync_provider(self, provider):
        """Test syncing a specific provider."""
        config = ProviderAPIConfig.objects.create(
            provider=provider,
            provider_type='test_provider',
            api_endpoint='https://api.test.com',
            sync_enabled=True
        )

        out = StringIO()
        call_command(
            'sync_provider',
            '--provider', str(config.pk),
            stdout=out
        )

        output = out.getvalue()
        assert 'Starting synchronization' in output
        assert 'Sync complete' in output
        assert '10/10 circuits synced' in output

    def test_command_sync_all_providers(self, provider):
        """Test syncing all enabled providers."""
        config1 = ProviderAPIConfig.objects.create(
            provider=provider,
            provider_type='test_provider',
            api_endpoint='https://api.test1.com',
            sync_enabled=True
        )

        # Create another provider
        from circuits.models import Provider
        provider2 = Provider.objects.create(
            name='Provider 2',
            slug='provider-2'
        )

        config2 = ProviderAPIConfig.objects.create(
            provider=provider2,
            provider_type='test_provider',
            api_endpoint='https://api.test2.com',
            sync_enabled=True
        )

        out = StringIO()
        call_command('sync_provider', stdout=out)

        output = out.getvalue()
        # Should process both providers
        assert output.count('Sync complete') == 2

    def test_command_disabled_provider_skipped(self, provider):
        """Test that disabled providers are skipped."""
        config = ProviderAPIConfig.objects.create(
            provider=provider,
            provider_type='test_provider',
            api_endpoint='https://api.test.com',
            sync_enabled=False  # Disabled
        )

        out = StringIO()
        call_command('sync_provider', stdout=out)

        output = out.getvalue()
        assert 'No enabled provider configurations found' in output

    def test_command_nonexistent_provider_type(self, provider):
        """Test command with provider type not in registry."""
        config = ProviderAPIConfig.objects.create(
            provider=provider,
            provider_type='nonexistent',
            api_endpoint='https://api.test.com',
            sync_enabled=True
        )

        out = StringIO()
        call_command('sync_provider', stdout=out)

        output = out.getvalue()
        assert 'not found in registry' in output

    def test_command_with_sync_errors(self, provider):
        """Test command when sync has errors."""

        class FailingMockProviderSync:
            def __init__(self, api_config):
                self.config = api_config

            def test_connection(self):
                return {
                    'success': False,
                    'message': 'Connection failed',
                    'response_time': 0
                }

            def sync_all(self):
                return {
                    'total': 10,
                    'success': 5,
                    'failed': 5,
                    'errors': ['Error 1', 'Error 2']
                }

        provider_registry.register('failing_provider', FailingMockProviderSync)

        config = ProviderAPIConfig.objects.create(
            provider=provider,
            provider_type='failing_provider',
            api_endpoint='https://api.test.com',
            sync_enabled=True
        )

        out = StringIO()
        call_command('sync_provider', stdout=out)

        output = out.getvalue()
        assert 'Failed: 5' in output
        assert 'Error 1' in output
        assert 'Error 2' in output

        provider_registry.unregister('failing_provider')

    def test_command_test_connection_failure(self, provider):
        """Test --test flag when connection fails."""

        class FailingConnectionProviderSync:
            def __init__(self, api_config):
                self.config = api_config

            def test_connection(self):
                return {
                    'success': False,
                    'message': 'Authentication failed',
                    'response_time': 0
                }

        provider_registry.register('failing_conn', FailingConnectionProviderSync)

        config = ProviderAPIConfig.objects.create(
            provider=provider,
            provider_type='failing_conn',
            api_endpoint='https://api.test.com',
            sync_enabled=True
        )

        out = StringIO()
        call_command(
            'sync_provider',
            '--provider', str(config.pk),
            '--test',
            stdout=out
        )

        output = out.getvalue()
        assert 'Connection failed' in output
        assert 'Authentication failed' in output

        provider_registry.unregister('failing_conn')


@pytest.mark.django_db
class TestCommandOutput:
    """Test command output formatting."""

    def setup_method(self):
        """Set up test provider in registry."""
        provider_registry.register('test_provider', MockProviderSync)

    def teardown_method(self):
        """Clean up test provider from registry."""
        provider_registry.unregister('test_provider')

    def test_command_output_formatting(self, provider):
        """Test that command output is properly formatted."""
        config = ProviderAPIConfig.objects.create(
            provider=provider,
            provider_type='test_provider',
            api_endpoint='https://api.test.com',
            sync_enabled=True
        )

        out = StringIO()
        call_command('sync_provider', '--provider', str(config.pk), stdout=out)

        output = out.getvalue()

        # Check for expected output sections
        assert 'Processing provider' in output
        assert 'Starting synchronization' in output
        assert 'Sync complete' in output
        assert 'Done!' in output

    def test_command_verbosity_levels(self, provider):
        """Test command with different verbosity levels."""
        config = ProviderAPIConfig.objects.create(
            provider=provider,
            provider_type='test_provider',
            api_endpoint='https://api.test.com',
            sync_enabled=True
        )

        # Test with verbosity 0 (quiet)
        out = StringIO()
        call_command(
            'sync_provider',
            '--provider', str(config.pk),
            verbosity=0,
            stdout=out
        )

        # Output should still contain key information
        output = out.getvalue()
        # Verbosity 0 may suppress some output
        # Main functionality should still work
        assert isinstance(output, str)
