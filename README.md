# NetBox Circuit Manager

A comprehensive NetBox plugin that extends the built-in circuit management functionality with advanced features for tracking costs, contracts, tickets, and circuit paths.

## Features

- **Financial Tracking**: Track Non-Recurring Charges (NRC) and Monthly Recurring Charges (MRC) for circuits
- **Contract Management**: Store contract terms, renewal dates, and upload contract documents
- **Ticket Integration**: Link support tickets to circuits for better tracking
- **Interactive Maps**: Upload KMZ files to visualize circuit paths on interactive maps
- **Provider API Integration**: Extensible framework to integrate with major carrier APIs for automated synchronization
- **REST API**: Full API support for all extended circuit data

## Requirements

- NetBox 4.5.0 or later
- Python 3.12, 3.13, or 3.14

## Installation

1. Install the plugin from PyPI:

```bash
pip install netbox-circuit-manager
```

2. Add the plugin to your `configuration.py`:

```python
PLUGINS = [
    'netbox_circuit_manager',
]

PLUGINS_CONFIG = {
    'netbox_circuit_manager': {
        'default_currency': 'USD',
        'enable_provider_sync': True,
    }
}
```

3. Run database migrations:

```bash
cd /opt/netbox/netbox/
python3 manage.py migrate netbox_circuit_manager
```

4. Restart NetBox:

```bash
sudo systemctl restart netbox
```

## Usage

### Financial Tracking

Navigate to a circuit in NetBox and you'll see additional tabs for:
- **Financial**: View and edit NRC/MRC charges
- **Contracts**: Manage contract terms and upload documents
- **Tickets**: Link support tickets to the circuit
- **Map**: Upload KMZ files to visualize the circuit path

### Provider API Integration

The plugin includes a framework for integrating with provider APIs. See the `providers/` directory for example implementations.

To create a custom provider integration:

1. Create a new provider class inheriting from `BaseProviderSync`
2. Implement the required methods for authentication and data synchronization
3. Register the provider in your NetBox configuration

Example providers included:
- Lumen (CenturyLink)
- AT&T
- Verizon
- Zayo

## API Endpoints

All circuit extensions are available via the NetBox REST API:

- `/api/plugins/circuit-manager/circuit-costs/`
- `/api/plugins/circuit-manager/circuit-contracts/`
- `/api/plugins/circuit-manager/circuit-tickets/`
- `/api/plugins/circuit-manager/circuit-paths/`

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and contribution guidelines.

## License

This project is licensed under the Apache License 2.0.

## Support

For issues and questions, please open an issue on GitHub.
