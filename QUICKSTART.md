# Quick Start Guide

Get up and running with NetBox Circuit Manager in 5 minutes.

## Installation

```bash
pip install netbox-circuit-manager
```

## Configuration

Add to your NetBox `configuration.py`:

```python
PLUGINS = ['netbox_circuit_manager']

PLUGINS_CONFIG = {
    'netbox_circuit_manager': {
        'default_currency': 'USD',
    }
}
```

## Run Migrations

```bash
cd /opt/netbox/netbox
python3 manage.py migrate netbox_circuit_manager
python3 manage.py collectstatic --no-input
sudo systemctl restart netbox netbox-rq
```

## Basic Usage

### 1. Add Cost Information to a Circuit

1. Navigate to **Circuits > Circuits**
2. Select a circuit
3. In the Circuit Manager section, click **Add Costs**
4. Fill in:
   - NRC (Non-Recurring Charge): One-time setup fee
   - MRC (Monthly Recurring Charge): Monthly service fee
   - Currency: USD, EUR, GBP, etc.
   - Billing Account: Provider's account number
5. Click **Save**

### 2. Upload a Contract

1. From the same circuit, click **Contracts** tab
2. Click **Add Contract**
3. Fill in:
   - Contract Number
   - Start/End Dates
   - Term in months
   - Auto-renew settings
   - Upload contract PDF
4. Click **Save**

### 3. Track Support Tickets

1. Click **Tickets** tab
2. Click **Add Ticket**
3. Fill in:
   - Ticket Number (from provider)
   - Subject and Description
   - Status and Priority
   - External URL (link to provider's ticket system)
4. Click **Save**

### 4. Visualize Circuit Path

1. Click **Circuit Path** tab
2. Click **Add Path**
3. Upload a KMZ file showing the circuit route
4. The map will automatically display the path
5. View path distance and route details

## Using the API

All circuit extensions are available via REST API:

### Get Circuit Costs

```bash
curl -H "Authorization: Token YOUR_TOKEN" \
  http://netbox/api/plugins/circuit-manager/circuit-costs/
```

### Get Circuit Contracts

```bash
curl -H "Authorization: Token YOUR_TOKEN" \
  http://netbox/api/plugins/circuit-manager/circuit-contracts/
```

### Get Circuit Tickets

```bash
curl -H "Authorization: Token YOUR_TOKEN" \
  http://netbox/api/plugins/circuit-manager/circuit-tickets/
```

### Create Circuit Cost via API

```bash
curl -X POST \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "circuit": 1,
    "nrc": 500.00,
    "mrc": 150.00,
    "currency": "USD"
  }' \
  http://netbox/api/plugins/circuit-manager/circuit-costs/
```

## Provider API Integration

### Set Up Provider Sync

1. Navigate to **Circuit Manager > Provider API Configs**
2. Click **Add**
3. Configure:
   - Select NetBox Provider
   - Choose Provider Type (Lumen, AT&T, etc.)
   - Enter API Endpoint URL
   - Add API Key and Secret
   - Enable Sync
   - Set Sync Interval
4. Click **Save**

### Test Connection

```bash
python3 manage.py sync_provider --provider 1 --test
```

### Run Manual Sync

```bash
python3 manage.py sync_provider --provider 1
```

### Set Up Automatic Sync (Cron)

```bash
# Edit crontab
sudo -u netbox crontab -e

# Add this line to sync every 6 hours
0 */6 * * * cd /opt/netbox/netbox && /opt/netbox/venv/bin/python manage.py sync_provider
```

## Common Workflows

### Workflow 1: New Circuit Onboarding

1. Create circuit in NetBox (standard NetBox process)
2. Add cost information (NRC/MRC)
3. Upload contract document
4. Add circuit path KMZ file
5. Link to any existing tickets

### Workflow 2: Contract Renewal Tracking

1. Search circuits by end date
2. Review contracts expiring soon
3. Update contract terms
4. Upload new contract documents
5. Update cost information if changed

### Workflow 3: Troubleshooting

1. Create ticket for circuit issue
2. Link to provider's ticket system
3. Track ticket status
4. Update resolution when closed
5. Review ticket history for patterns

## Tips

- **Currency Consistency**: Use the same currency code throughout for accurate reporting
- **Contract Dates**: Set end dates for contract tracking and renewal alerts
- **KMZ Files**: Get circuit path KMZ files from providers (Google Earth format)
- **API Sync**: Enable automatic sync to keep costs and status up to date
- **Bulk Operations**: Use the API for bulk updates across multiple circuits

## Next Steps

- [Full Installation Guide](INSTALLATION.md)
- [Provider Integration Guide](PROVIDER_INTEGRATION.md)
- [Contributing Guide](CONTRIBUTING.md)
- [API Documentation](http://your-netbox/api/docs/)

## Getting Help

- Check [GitHub Issues](https://github.com/yourusername/netbox-circuit-manager/issues)
- Review [NetBox Documentation](https://netboxlabs.com/docs/)
- Join [NetBox Community Slack](https://netdev.chat/)

## Example KMZ File

To create a KMZ file for testing:

1. Open Google Earth
2. Draw a path between circuit endpoints
3. Right-click the path > Save Place As
4. Save as KMZ format
5. Upload to NetBox Circuit Manager

The plugin will automatically parse the KMZ and display it on an interactive map.
