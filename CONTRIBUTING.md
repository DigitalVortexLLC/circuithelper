# Contributing to NetBox Circuit Manager

Thank you for your interest in contributing to NetBox Circuit Manager.

## Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/DigitalVortexLLC/circuithelper.git
cd circuithelper
```

### 2. Set Up Development Environment

You'll need a working NetBox installation for development. The easiest way is using Docker:

```bash
# Clone NetBox
git clone https://github.com/netbox-community/netbox-docker.git
cd netbox-docker

# Create docker-compose override for plugin development
cat > docker-compose.override.yml <<EOF
version: '3.4'
services:
  netbox:
    volumes:
      - /path/to/circuithelper:/opt/circuithelper:ro
    environment:
      PLUGINS: circuithelper
EOF

# Start NetBox
docker-compose up -d
```

### 3. Install Plugin in Development Mode

```bash
# Enter NetBox container
docker-compose exec netbox bash

# Install plugin in editable mode
pip install -e /opt/circuithelper

# Run migrations
python manage.py migrate circuithelper

# Create superuser
python manage.py createsuperuser

# Exit container
exit
```

### 4. Access NetBox

Navigate to http://localhost:8000 and log in with your superuser credentials.

## Making Changes

### Code Style

We follow PEP 8 style guidelines. Use tools like `black` and `flake8`:

```bash
pip install black flake8
black circuithelper/
flake8 circuithelper/
```

### Database Migrations

When you modify models, create migrations:

```bash
python manage.py makemigrations circuithelper
python manage.py migrate circuithelper
```

### Testing

Write tests for new features:

```bash
# Run tests
python manage.py test circuithelper

# Run with coverage
coverage run --source='circuithelper' manage.py test circuithelper
coverage report
```

## Submitting Changes

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Commit Your Changes

Use clear, descriptive commit messages:

```bash
git add .
git commit -m "Add support for XYZ feature"
```

### 3. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub.

## Pull Request Guidelines

- Include tests for new features
- Update documentation as needed
- Follow existing code style
- Keep changes focused and atomic
- Reference any related issues

## Adding New Provider Integrations

See [PROVIDER_INTEGRATION.md](PROVIDER_INTEGRATION.md) for detailed instructions on creating provider integrations.

### Provider Contribution Checklist

- [ ] Create provider class extending `BaseProviderSync`
- [ ] Implement all required methods
- [ ] Register provider in registry
- [ ] Add provider to `PROVIDER_CHOICES` in models
- [ ] Write unit tests
- [ ] Add documentation with example usage
- [ ] Test with real API (if possible)

## Reporting Bugs

When reporting bugs, please include:

- NetBox version
- Plugin version
- Python version
- Steps to reproduce
- Expected vs actual behavior
- Relevant log output
- Screenshots (if applicable)

## Feature Requests

Feature requests are welcome. Please include:

- Clear description of the feature
- Use case / why it's needed
- Example of how it would work
- Any relevant references or similar implementations

## Code Review Process

All submissions require review. We'll:

1. Review code for style and quality
2. Test functionality
3. Check for breaking changes
4. Verify documentation updates
5. Provide feedback or merge

## Community

- GitHub Issues: Bug reports and feature requests
- GitHub Discussions: Questions and general discussion
- NetBox Community Slack: Real-time chat

## License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.
