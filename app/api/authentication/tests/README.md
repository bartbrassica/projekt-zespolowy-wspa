# Digital Lockbox API Tests

This directory contains the test suite for the Digital Lockbox API.

## Structure

```
tests/
├── conftest.py              # Pytest configuration and fixtures
├── test_setup.py            # Basic setup verification tests
├── unit/                    # Unit tests
│   ├── test_models.py       # Model tests
│   ├── test_services.py     # Service layer tests
│   └── test_utils.py        # Utility function tests
├── integration/             # Integration tests
│   ├── test_auth_endpoints.py      # Authentication endpoint tests
│   └── test_password_endpoints.py  # Password management endpoint tests
└── fixtures/                # Test fixtures and factories
    ├── factories.py         # Factory Boy model factories
    └── __init__.py

```

## Running Tests

### Prerequisites

1. Install test dependencies:
   ```bash
   cd digitalockbox_api
   pip install -e ".[test]"
   ```

2. Ensure PostgreSQL is running (via Docker Compose):
   ```bash
   docker-compose up -d db
   ```

### Run All Tests

```bash
# From the digitalockbox_api directory
pytest

# Or with more verbose output
pytest -v

# Run specific test markers
pytest -m unit          # Run only unit tests
pytest -m integration   # Run only integration tests
pytest -m auth          # Run only authentication tests
pytest -m password      # Run only password management tests
```

### Run Specific Test Files

```bash
# Run a specific test file
pytest authentication/tests/unit/test_models.py

# Run a specific test class
pytest authentication/tests/unit/test_models.py::TestUserModel

# Run a specific test function
pytest authentication/tests/unit/test_models.py::TestUserModel::test_create_user
```

### Run Tests in Parallel

```bash
# Run tests using multiple CPU cores
pytest -n auto
```

## Coverage Reports

### Generate Coverage Report

```bash
# Run tests with coverage
pytest --cov=authentication --cov-report=html --cov-report=term-missing

# Open HTML coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### Coverage Configuration

Coverage settings are configured in:
- `pyproject.toml` - Main pytest and coverage configuration
- `.coveragerc` - Additional coverage settings
- `pytest.ini` - Pytest-specific configuration

## Test Markers

Tests are organized using pytest markers:

- `@pytest.mark.unit` - Unit tests (fast, isolated)
- `@pytest.mark.integration` - Integration tests (slower, may hit DB/external services)
- `@pytest.mark.slow` - Slow running tests
- `@pytest.mark.auth` - Authentication related tests
- `@pytest.mark.password` - Password management tests

Example usage:
```python
@pytest.mark.unit
@pytest.mark.auth
def test_user_creation():
    # Test code here
    pass
```

## Fixtures

Common fixtures are defined in `conftest.py`:

### User Fixtures
- `user` - Standard verified, active user
- `verified_user` - Explicitly verified user
- `unverified_user` - User with unverified email
- `inactive_user` - Inactive user account
- `multiple_users` - List of 3 test users

### Token Fixtures
- `verification_token` - Email verification token
- `password_reset_token` - Password reset token
- `expired_token` - Expired token for testing
- `access_token` - Valid JWT access token
- `refresh_token` - Valid JWT refresh token

### Password Management Fixtures
- `password_entry` - Basic password entry
- `password_folder` - Password folder
- `password_tag` - Password tag
- `password_share_link` - Share link for password

### Client Fixtures
- `api_client` - Django test client
- `authenticated_client` - Client with auth header set

### Other Fixtures
- `test_password` - Standard test password ("TestPassword123!")
- `test_master_password` - Standard master password ("MasterPassword123!")
- `mock_request` - Mock HTTP request object
- `clear_emails` - Clears email outbox before/after tests

## Factory Boy

Model factories are defined in `fixtures/factories.py`. Use them to create test data:

```python
from authentication.tests.fixtures.factories import (
    UserFactory,
    PasswordEntryFactory,
    PasswordFolderFactory,
)

def test_something():
    # Create a user
    user = UserFactory()

    # Create a user with specific attributes
    admin = UserFactory(is_staff=True, email="admin@example.com")

    # Create multiple users
    users = UserFactory.create_batch(5)

    # Create a password entry for a user
    entry = PasswordEntryFactory(user=user)
```

Available factories:
- `UserFactory` - Standard user
- `UnverifiedUserFactory` - Unverified user
- `InactiveUserFactory` - Inactive user
- `TokenFactory` - Generic token
- `VerificationTokenFactory` - Email verification token
- `PasswordResetTokenFactory` - Password reset token
- `RefreshTokenFactory` - JWT refresh token
- `ExpiredTokenFactory` - Expired token
- `PasswordEntryFactory` - Password entry
- `PasswordEntryWithExpirationFactory` - Password entry with expiration
- `ExpiredPasswordEntryFactory` - Expired password entry
- `FavoritePasswordEntryFactory` - Favorite password entry
- `PasswordFolderFactory` - Password folder
- `PasswordTagFactory` - Password tag
- `PasswordShareLinkFactory` - Share link
- `PasswordAccessLogFactory` - Access log entry

## Writing Tests

### Example Unit Test

```python
import pytest
from authentication.models import User

@pytest.mark.unit
def test_user_creation(db):
    """Test creating a user."""
    user = User.objects.create_user(
        email="test@example.com",
        password="TestPassword123!"
    )

    assert user.email == "test@example.com"
    assert user.check_password("TestPassword123!")
    assert user.is_active
```

### Example Integration Test

```python
import pytest
from django.urls import reverse

@pytest.mark.integration
@pytest.mark.auth
def test_user_registration(api_client, clear_emails):
    """Test user registration endpoint."""
    url = reverse("api:auth_register")
    data = {
        "email": "newuser@example.com",
        "password": "SecurePass123!",
        "first_name": "New",
        "last_name": "User"
    }

    response = api_client.post(url, data, content_type="application/json")

    assert response.status_code == 201
    assert response.json()["email"] == "newuser@example.com"
```

## Continuous Integration

Tests should be run in CI/CD pipelines. Example GitHub Actions workflow:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          pip install -e ".[test]"

      - name: Run tests
        run: |
          pytest --cov=authentication --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## Best Practices

1. **Isolation**: Each test should be independent and not rely on other tests
2. **Fixtures**: Use fixtures for common setup code
3. **Factories**: Use Factory Boy for creating test data
4. **Markers**: Tag tests appropriately with markers
5. **Naming**: Use descriptive test names that explain what is being tested
6. **Assertions**: Use clear, specific assertions
7. **Coverage**: Aim for >80% code coverage
8. **Speed**: Keep unit tests fast, use integration tests for slower operations

## Troubleshooting

### Database Connection Issues

If you get database connection errors:
```bash
# Make sure PostgreSQL is running
docker-compose up -d db

# Check if the database port is correct
docker-compose ps
```

### Import Errors

If you get import errors:
```bash
# Make sure you're in the correct directory
cd digitalockbox_api

# Install the package in development mode
pip install -e ".[test]"
```

### Coverage Not Working

If coverage isn't being collected:
```bash
# Make sure pytest-cov is installed
pip install pytest-cov

# Run with explicit coverage commands
pytest --cov=authentication --cov-report=term-missing
```
