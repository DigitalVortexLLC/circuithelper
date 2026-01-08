# Installation Guide

## Prerequisites

- NetBox 4.5.0 or later
- Python 3.12, 3.13, or 3.14
- PostgreSQL database
- Redis

## Installation Steps

### 1. Install the Plugin

#### From Source (Development)

```bash
cd /opt
git clone https://github.com/yourusername/circuithelper.git
cd circuithelper
pip install -e .
```

#### From PyPI (Production)

```bash
pip install circuithelper
```

### 2. Configure NetBox

Edit your NetBox `configuration.py` file (usually located at `/opt/netbox/netbox/netbox/configuration.py`):

```python
# Enable the plugin
PLUGINS = [
    'circuithelper',
]

# Optional plugin configuration
PLUGINS_CONFIG = {
    'circuithelper': {
        # Default currency for cost tracking
        'default_currency': 'USD',

        # Enable provider API synchronization
        'enable_provider_sync': True,

        # Supported currencies
        'supported_currencies': ['USD', 'EUR', 'GBP', 'CAD', 'AUD'],
    }
}
```

### 3. Run Database Migrations

```bash
cd /opt/netbox/netbox
python3 manage.py migrate circuithelper
```

### 4. Collect Static Files

```bash
python3 manage.py collectstatic --no-input
```

### 5. Restart NetBox Services

```bash
sudo systemctl restart netbox netbox-rq
```

## Verify Installation

1. Log into NetBox
2. You should see a "Circuit Manager" menu item in the navigation
3. Navigate to a circuit and you should see new tabs for Costs, Contracts, Tickets, and Map

## File Upload Configuration

To enable file uploads for contracts and KMZ files, ensure your NetBox installation has the MEDIA_ROOT configured:

```python
# configuration.py
MEDIA_ROOT = '/opt/netbox/netbox/media/'
```

Make sure the directory exists and is writable by the NetBox user:

```bash
sudo mkdir -p /opt/netbox/netbox/media/circuit_contracts
sudo mkdir -p /opt/netbox/netbox/media/circuit_paths
sudo chown -R netbox:netbox /opt/netbox/netbox/media/
```

## Provider API Integration Setup

To set up provider API integrations:

1. Navigate to **Circuit Manager > Provider API Configs**
2. Click **Add**
3. Select the provider and configure:
   - Provider Type (Lumen, AT&T, Verizon, Zayo, or Custom)
   - API Endpoint URL
   - API Key and Secret
   - Sync settings

4. Test the connection:

```bash
python3 manage.py sync_provider --provider <config_id> --test
```

5. Run initial sync:

```bash
python3 manage.py sync_provider --provider <config_id>
```

## Automated Sync with Cron

To automatically sync provider data, add a cron job:

```bash
# Edit crontab for netbox user
sudo -u netbox crontab -e

# Add this line to sync every 6 hours
0 */6 * * * cd /opt/netbox/netbox && /opt/netbox/venv/bin/python manage.py sync_provider
```

## Troubleshooting

### Plugin Not Appearing

- Verify the plugin is installed: `pip list | grep circuithelper`
- Check NetBox logs: `sudo journalctl -u netbox -f`
- Ensure migrations ran successfully

### File Upload Issues

- Check directory permissions
- Verify MEDIA_ROOT is configured
- Check web server (nginx/Apache) configuration for media serving

### API Sync Issues

- Test connection using `--test` flag
- Check API credentials
- Review sync logs in NetBox admin panel
- Verify firewall rules allow outbound connections to provider APIs

## Upgrading

To upgrade to a newer version:

```bash
pip install --upgrade circuithelper
python3 manage.py migrate circuithelper
python3 manage.py collectstatic --no-input
sudo systemctl restart netbox netbox-rq
```

## Uninstallation

To remove the plugin:

```bash
# Remove from configuration.py PLUGINS list
# Then run:
python3 manage.py migrate circuithelper zero
pip uninstall circuithelper
sudo systemctl restart netbox netbox-rq
```

**Warning:** Uninstalling will delete all Circuit Manager data including costs, contracts, tickets, and paths.
