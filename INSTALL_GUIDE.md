# CircuitHelper Installation Guide

## Prerequisites

CircuitHelper is a NetBox plugin and requires an existing NetBox installation (v4.5.0 or higher).

### Important Notes

- **NetBox is NOT installed via pip** - It's a full Django application that must be set up separately
- This plugin must be installed into an existing NetBox installation
- The `requirements.txt` file contains only the plugin's dependencies, not NetBox itself

## Installation Options

### Option 1: Install into Existing NetBox (Production/Testing)

If you have NetBox already installed and running:

1. **Activate your NetBox virtual environment:**
   ```bash
   source /opt/netbox/venv/bin/activate  # Adjust path to your NetBox installation
   ```

2. **Install the plugin:**
   ```bash
   pip install circuithelper
   ```

   Or for development installation:
   ```bash
   pip install -e /path/to/circuithelper
   ```

3. **Update NetBox configuration** (`/opt/netbox/netbox/netbox/configuration.py`):
   ```python
   PLUGINS = [
       'circuithelper',
   ]

   PLUGINS_CONFIG = {
       'circuithelper': {
           'default_currency': 'USD',
           'enable_provider_sync': True,
           'supported_currencies': ['USD', 'EUR', 'GBP', 'CAD', 'AUD'],
       }
   }
   ```

4. **Run migrations:**
   ```bash
   cd /opt/netbox/netbox
   python3 manage.py migrate circuithelper
   ```

5. **Collect static files:**
   ```bash
   python3 manage.py collectstatic --no-input
   ```

6. **Restart NetBox services:**
   ```bash
   sudo systemctl restart netbox netbox-rq
   ```

### Option 2: Development Setup (Without Full NetBox)

For plugin development and testing without a full NetBox installation:

1. **Install plugin dependencies only:**
   ```bash
   cd /path/to/circuithelper
   pip3 install -r requirements.txt
   ```

   ✅ **This is what you just did!**

2. **Install development dependencies:**
   ```bash
   pip3 install -r requirements-dev.txt
   ```

3. **For full testing**, you'll still need to set up NetBox in development mode:
   - Follow the [NetBox Development Guide](https://netbox.readthedocs.io/en/stable/development/)
   - Clone NetBox and set up a development environment
   - Install your plugin into the NetBox development environment

### Option 3: Docker Development Environment

Use Docker to set up a NetBox development environment with your plugin:

1. **Create a docker-compose.yml** (see NetBox documentation)
2. **Mount your plugin directory** as a volume
3. **Install the plugin** in the NetBox container

## Verification

After installation, verify the plugin is loaded:

```bash
# From your NetBox directory
python3 manage.py nbshell

# In the shell:
from django.apps import apps
print(apps.get_app_config('circuithelper'))
```

## What Was Just Installed

When you ran `pip3 install -r requirements.txt`, you installed these plugin dependencies:

- ✅ `fastkml>=1.0.0` - For KMZ file parsing
- ✅ `lxml>=4.9.0` - XML parsing (required by fastkml)
- ✅ `shapely>=2.0.0` - Geospatial data handling
- ✅ `folium>=0.15.0` - Interactive map generation
- ✅ `requests>=2.31.0` - HTTP requests for provider API integration

These packages are available in your Python environment and can be used for development.

## Next Steps

### For Plugin Development (Current Setup)
You can now:
- ✅ Edit plugin code
- ✅ Run code quality checks (`black`, `flake8`)
- ✅ Write unit tests
- ⚠️  **Cannot run Django/NetBox-specific tests** (requires NetBox installation)

### For Full Testing
To run the full test suite and see the plugin in action:
1. Set up a NetBox development environment
2. Install this plugin into that environment
3. Run `pytest` with NetBox available

## Troubleshooting

### Error: "No module named 'netbox'"
This is expected if you're developing without a full NetBox installation. NetBox must be installed separately for full functionality.

### Error: "No matching distribution found for netbox"
NetBox is not available on PyPI. See the [Official NetBox Installation Guide](https://docs.netbox.dev/en/stable/installation/).

## References

- [NetBox Plugin Development Documentation](https://docs.netbox.dev/en/stable/plugins/development/)
- [NetBox Installation Guide](https://docs.netbox.dev/en/stable/installation/)
- [CircuitHelper README](README.md)
- [CircuitHelper Quick Start](QUICKSTART.md)
