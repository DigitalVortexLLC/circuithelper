# NetBox Circuit Manager - Project Overview

## Summary

A comprehensive NetBox plugin that extends the built-in circuit management functionality with advanced features for tracking costs, contracts, tickets, geographic paths, and provider API integration.

## Version

- **Current Version**: 0.1.0
- **NetBox Compatibility**: 4.5.0+
- **Python Compatibility**: 3.12, 3.13, 3.14

## Key Features

### 1. Financial Tracking (NRC/MRC)
- Track Non-Recurring Charges (installation/setup fees)
- Track Monthly Recurring Charges (service fees)
- Multi-currency support (USD, EUR, GBP, CAD, AUD)
- Billing account association
- Cost history tracking

### 2. Contract Management
- Store contract terms and conditions
- Track start/end dates and renewal periods
- Auto-renewal settings
- Early termination fee tracking
- Contract document upload (PDF, etc.)
- Contract expiration alerts

### 3. Ticket Integration
- Link support tickets to circuits
- Track ticket status (Open, In Progress, Pending, Resolved, Closed)
- Priority levels (Low, Medium, High, Critical)
- External ticket system integration (URLs)
- Ticket history and resolution tracking

### 4. Interactive Circuit Path Maps
- Upload KMZ files (Google Earth format)
- Automatic parsing to GeoJSON
- Interactive map visualization using Folium
- Path distance calculation
- Geographic center point auto-detection
- Zoom level configuration

### 5. Provider API Integration Framework
- Extensible architecture for carrier API integrations
- Base class for easy provider implementation
- Built-in example: Lumen provider
- Automatic data synchronization
- Configurable sync intervals
- Connection testing utilities
- Management command for manual/automated sync

### 6. REST API
- Full CRUD operations for all models
- Nested circuit relationships
- Token authentication
- OpenAPI/Swagger documentation
- Filtering and pagination support

## Project Structure

```
netbox_circuit_manager/
├── setup.py                          # Package setup and dependencies
├── requirements.txt                  # Python dependencies
├── MANIFEST.in                       # Package manifest
├── LICENSE                           # Apache 2.0 license
├── .gitignore                        # Git ignore rules
│
├── README.md                         # Main documentation
├── QUICKSTART.md                     # Quick start guide
├── INSTALLATION.md                   # Detailed installation guide
├── PROVIDER_INTEGRATION.md           # Provider API integration guide
├── CONTRIBUTING.md                   # Contribution guidelines
├── PROJECT_OVERVIEW.md               # This file
│
└── netbox_circuit_manager/           # Main plugin package
    ├── __init__.py                   # Plugin configuration (PluginConfig)
    ├── models.py                     # Database models (5 models)
    ├── forms.py                      # Django forms
    ├── views.py                      # View classes and functions
    ├── urls.py                       # URL routing
    ├── navigation.py                 # NetBox menu integration
    ├── utils.py                      # Utility functions (KMZ parsing, etc.)
    │
    ├── api/                          # REST API
    │   ├── __init__.py
    │   ├── serializers.py            # DRF serializers
    │   ├── views.py                  # API viewsets
    │   └── urls.py                   # API routing
    │
    ├── migrations/                   # Database migrations
    │   └── __init__.py
    │
    ├── templates/                    # HTML templates
    │   └── netbox_circuit_manager/
    │       └── circuit_detail_tab.html
    │
    ├── static/                       # Static assets
    │   └── netbox_circuit_manager/
    │       ├── css/
    │       └── js/
    │
    ├── management/                   # Django management commands
    │   ├── __init__.py
    │   └── commands/
    │       ├── __init__.py
    │       └── sync_provider.py      # Provider sync command
    │
    └── providers/                    # Provider API integration framework
        ├── __init__.py
        ├── base.py                   # BaseProviderSync abstract class
        ├── registry.py               # Provider registry
        └── lumen.py                  # Example: Lumen provider integration
```

## Database Models

### 1. CircuitCost
- **Purpose**: Track NRC/MRC for circuits
- **Key Fields**: nrc, mrc, currency, billing_account
- **Relationship**: OneToOne with Circuit

### 2. CircuitContract
- **Purpose**: Manage contract terms and documents
- **Key Fields**: contract_number, start_date, end_date, term_months, auto_renew, contract_file
- **Relationship**: ForeignKey to Circuit (one circuit can have multiple contracts)

### 3. CircuitTicket
- **Purpose**: Track support tickets
- **Key Fields**: ticket_number, subject, status, priority, description, external_url
- **Relationship**: ForeignKey to Circuit

### 4. CircuitPath
- **Purpose**: Store geographic path data
- **Key Fields**: kmz_file, geojson_data, map_center_lat, map_center_lon, path_distance_km
- **Relationship**: OneToOne with Circuit

### 5. ProviderAPIConfig
- **Purpose**: Configure provider API integrations
- **Key Fields**: provider_type, api_endpoint, api_key, api_secret, sync_enabled
- **Relationship**: ForeignKey to Provider

## API Endpoints

All endpoints are under `/api/plugins/circuit-manager/`:

- `/circuit-costs/` - Circuit cost management
- `/circuit-contracts/` - Contract management
- `/circuit-tickets/` - Ticket tracking
- `/circuit-paths/` - Circuit path data
- `/provider-api-configs/` - Provider API configurations

## Management Commands

### sync_provider
Synchronize circuit data from provider APIs.

```bash
# Test connection
python manage.py sync_provider --provider <id> --test

# Sync specific provider
python manage.py sync_provider --provider <id>

# Sync all enabled providers
python manage.py sync_provider
```

## Provider Integration Framework

### BaseProviderSync Abstract Class
Base class for all provider integrations.

**Required Methods:**
- `authenticate()` - Authenticate with provider API
- `get_circuits()` - Retrieve circuit list
- `get_circuit_details()` - Get circuit details
- `sync_circuit_costs()` - Sync cost data

**Optional Methods:**
- `sync_circuit_tickets()` - Sync ticket data
- `sync_circuit_path()` - Sync path data
- `_match_circuit()` - Custom circuit matching logic

### Provider Registry
Centralized registry for provider implementations.

**Usage:**
```python
from netbox_circuit_manager.providers import provider_registry

# Register a provider
provider_registry.register('mycarrier', MyCarrierProviderSync)

# Get a provider
provider_class = provider_registry.get('mycarrier')
```

## Technology Stack

### Core Dependencies
- **NetBox**: 4.5.0+ (Django-based IPAM/DCIM)
- **Django**: (via NetBox)
- **Django REST Framework**: (via NetBox)

### Additional Libraries
- **fastkml**: 1.0.0+ (KML/KMZ parsing)
- **lxml**: 4.9.0+ (XML processing)
- **shapely**: 2.0.0+ (Geospatial operations)
- **folium**: 0.15.0+ (Interactive maps)
- **requests**: 2.31.0+ (HTTP client for provider APIs)

## File Uploads

### Supported File Types

**Contracts:**
- PDF documents
- Microsoft Word documents
- Any contract-related files

**Circuit Paths:**
- KMZ files (Keyhole Markup Language - Google Earth format)
- Automatically parsed to GeoJSON for map rendering

### Storage Location
- Contracts: `media/circuit_contracts/YYYY/MM/`
- Paths: `media/circuit_paths/YYYY/MM/`

## Security Considerations

1. **API Credentials**: Provider API secrets should be encrypted at rest
2. **File Uploads**: Validated file types and size limits
3. **Authentication**: Uses NetBox's built-in authentication
4. **Permissions**: Leverages NetBox's RBAC system
5. **HTTPS**: All provider API calls use HTTPS

## Performance Considerations

1. **Database Indexing**: Key fields indexed for fast queries
2. **API Pagination**: Large result sets paginated
3. **Async Processing**: Provider sync runs as background task
4. **Caching**: Map HTML cached to reduce generation overhead
5. **Efficient Queries**: Uses select_related/prefetch_related

## Future Enhancements

Potential features for future versions:

- [ ] Email alerts for contract expiration
- [ ] Cost reporting and analytics dashboard
- [ ] Circuit capacity planning tools
- [ ] Additional provider integrations (AT&T, Verizon, Zayo)
- [ ] Webhook notifications for ticket updates
- [ ] Circuit health monitoring integration
- [ ] SLA tracking and reporting
- [ ] Batch import/export utilities
- [ ] GraphQL API support

## Documentation

- **README.md**: Overview and basic usage
- **QUICKSTART.md**: 5-minute getting started guide
- **INSTALLATION.md**: Detailed installation instructions
- **PROVIDER_INTEGRATION.md**: Guide for creating provider integrations
- **CONTRIBUTING.md**: Development and contribution guidelines
- **PROJECT_OVERVIEW.md**: This comprehensive overview

## Support and Community

- **Issues**: GitHub Issues for bug reports
- **Discussions**: GitHub Discussions for questions
- **Contributions**: Pull requests welcome
- **License**: Apache 2.0

## Credits

Built for NetBox 4.5+ using the NetBox plugin framework.

## Changelog

### Version 0.1.0 (Initial Release)
- Circuit cost tracking (NRC/MRC)
- Contract management with file uploads
- Ticket integration
- KMZ circuit path visualization
- Provider API integration framework
- Lumen provider example
- REST API for all models
- Management command for provider sync
- Comprehensive documentation
