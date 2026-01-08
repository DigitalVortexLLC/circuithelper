from netbox.plugins import PluginConfig


class CircuitManagerConfig(PluginConfig):
    name = 'circuithelper'
    verbose_name = 'Circuit Manager'
    description = 'Advanced circuit management with cost tracking, contracts, and provider API integration'
    version = '0.1.0'
    author = 'Your Name'
    author_email = 'your.email@example.com'
    base_url = 'circuit-manager'
    required_settings = []
    default_settings = {
        'default_currency': 'USD',
        'enable_provider_sync': True,
        'supported_currencies': ['USD', 'EUR', 'GBP', 'CAD', 'AUD'],
    }
    min_version = '4.5.0'


config = CircuitManagerConfig
