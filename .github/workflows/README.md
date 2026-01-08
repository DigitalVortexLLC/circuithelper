# GitHub Actions Workflows

This directory contains CI/CD workflows for the CircuitHelper NetBox plugin.

## Workflows

### 1. `lint.yml` - Code Quality & Security (Fast)

**Runs on**: Every push and pull request
**Duration**: ~2-3 minutes
**Purpose**: Quick feedback on code quality

This workflow runs without requiring a full NetBox installation, making it fast and efficient for development.

**Jobs**:
- **lint**: Checks code formatting and style
  - `flake8`: Linting (uses `.flake8` configuration)
  - `black`: Code formatting
  - `isort`: Import sorting

- **security**: Security scanning
  - `safety`: Checks for known vulnerabilities in dependencies
  - `bandit`: Static security analysis of Python code

### 2. `tests.yml` - Integration Tests (Slow)

**Runs on**: Every push and pull request
**Duration**: ~10-15 minutes
**Purpose**: Full integration testing with NetBox

This workflow sets up a complete NetBox environment and runs the plugin's test suite.

**Jobs**:
- **test**: Runs plugin tests in a NetBox environment
  - Clones NetBox from GitHub
  - Sets up PostgreSQL and Redis services
  - Configures NetBox with the plugin
  - Runs migrations
  - Executes Django tests

**Note**: This workflow requires a full NetBox installation, which is why it takes longer.

## Understanding the Workflows

### Why Two Separate Workflows?

**Problem**: NetBox is not available as a pip package, so we can't simply run `pip install netbox`. This makes testing NetBox plugins more complex than testing regular Python packages.

**Solution**:
- **lint.yml**: Fast feedback on code quality without NetBox
- **tests.yml**: Full integration tests with a real NetBox environment

### Development Workflow

1. **Write code** → Push to branch
2. **lint.yml runs** (~2 min) → Get quick feedback on formatting/security
3. **tests.yml runs** (~10 min) → Verify plugin works with NetBox

If `lint.yml` fails, you can fix issues quickly without waiting for the full test suite.

## Fixing Common Issues

### ❌ "No module named 'netbox'"

**Cause**: Trying to run tests without a NetBox installation
**Solution**: Tests must run inside a NetBox environment (handled by `tests.yml`)

### ❌ "ERROR: No matching distribution found for netbox"

**Cause**: Attempting `pip install netbox` (NetBox is not on PyPI)
**Solution**: Clone NetBox from GitHub instead (already done in `tests.yml`)

### ❌ Flake8 failures

**Cause**: Code doesn't meet style guidelines
**Solution**:
```bash
# Auto-fix formatting
black circuithelper/
isort circuithelper/

# Check remaining issues
flake8 circuithelper/
```

### ❌ Tests fail in GitHub Actions but pass locally

**Cause**: Different NetBox versions or missing dependencies
**Solution**: Check the NetBox version matrix in `tests.yml` line 15

## Running Workflows Locally

### Running Lint Checks Locally

```bash
# Install tools
pip install flake8 black isort

# Run checks
flake8 circuithelper/
black --check circuithelper/
isort --check-only circuithelper/

# Auto-fix
black circuithelper/
isort circuithelper/
```

### Running Tests Locally

You need a NetBox installation. See [INSTALL_GUIDE.md](../../INSTALL_GUIDE.md) for options:

1. **Option 1**: Install into an existing NetBox instance
2. **Option 2**: Set up NetBox development environment
3. **Option 3**: Use Docker with NetBox

## Modifying the Workflows

### Testing Against Different NetBox Versions

Edit `tests.yml` line 15:

```yaml
matrix:
  python-version: ['3.12', '3.13', '3.14']
  netbox-version: ['4.5.0', '4.6.0']  # Add more versions here
```

### Adding New Linting Tools

Edit `lint.yml` and add a new step:

```yaml
- name: Run mypy type checking
  run: |
    pip install mypy
    mypy circuithelper/
```

### Disabling Tests Temporarily

Add `if: false` to disable a job:

```yaml
test:
  if: false  # Temporarily disable this job
  runs-on: ubuntu-latest
  ...
```

## Workflow Status Badges

Add to your README.md:

```markdown
![Lint](https://github.com/YOUR_ORG/circuithelper/workflows/Lint/badge.svg)
![Tests](https://github.com/YOUR_ORG/circuithelper/workflows/Tests/badge.svg)
```

## References

- [NetBox Plugin Development](https://docs.netbox.dev/en/stable/plugins/development/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Testing Django Applications](https://docs.djangoproject.com/en/stable/topics/testing/)
