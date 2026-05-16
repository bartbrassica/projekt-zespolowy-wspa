# Digital Lockbox

A secure password management application with a Django REST API backend and React frontend, containerized with Docker.

## Architecture

- **API**: Django + Django Ninja REST framework with JWT authentication
- **GUI**: React + TypeScript + Vite + TailwindCSS
- **Database**: PostgreSQL 16
- **Deployment**: Docker + Docker Compose

## Prerequisites

- Docker
- Docker Compose
- Git

## Setup

### 1. Clone the repositories

```bash
# Clone the main repository
git clone https://github.com/bartbrassica/digitallockbox.git
cd inz

# Clone the API
git clone https://github.com/bartbrassica/digitalockbox_api.git

# Clone the GUI
git clone https://github.com/bartbrassica/digitalockbox_gui.git

```

### 2. Configure environment variables

Copy the example environment file and configure your settings:

```bash
cp .env.example .env
```

Edit `.env` with your desired configuration:

```env
# Database Configuration
DB_NAME=lockbox1
DB_USER=postgres
DB_PASSWORD=your-secure-password

# Django Configuration
CLIENT_SECRET=your-very-secure-secret-key-here
DEBUG=False
JWT_ALG=ES512

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com

# Frontend Configuration
FRONTEND_URL=http://localhost:3000
```

**Important**:
- Generate a strong `CLIENT_SECRET` for production
- For Gmail, use an [App Password](https://support.google.com/accounts/answer/185833)
- Set `DEBUG=False` in production

### 3. Run with Task

Build and start all services:

```bash
go-task up
```

Or use docker-compose directly:

```bash
docker-compose up -d --build
```

### 4. Access the application

- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/docs
- **Database**: localhost:5433 (PostgreSQL)

## Development

### Quick Reference

```bash
# View all available commands
go-task --list

# Start services
go-task up

# Stop services
go-task down

# View logs (all services)
go-task logs

# View logs for specific service
go-task logs SERVICE=api
go-task logs SERVICE=gui

# Database management
go-task db-up           # Start database
go-task db-down         # Stop database
go-task db-reset        # Reset database (removes all data)

# Build services
go-task build

# Django commands
go-task migrate         # Run migrations
go-task makemigrations  # Create new migrations
go-task shell           # Open shell in API container
```

## Project Structure

```
inz/
├── digitalockbox_api/       # Django API backend
│   ├── authentication/      # Django app
│   ├── Dockerfile
│   └── pyproject.toml
├── digitalockbox_gui/       # React frontend
│   ├── src/
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
├── docker-compose.yml       # Docker orchestration
├── .env                     # Environment variables (create from .env.example)
├── .env.example            # Environment template
└── README.md               # This file
```

## Services

### Database (PostgreSQL)

- Image: `postgres:16-alpine`
- Port: `5433:5432` (host:container)
- Data persisted in Docker volume: `postgres_data`

### API (Django)

- Python 3.12.9
- Runs migrations automatically on startup
- Port: `8000:8000`
- Hot reload enabled in development

### GUI (React + Nginx)

- Node 20 for building
- Nginx for serving static files
- Port: `3000:80`
- API requests proxied to backend

## Troubleshooting

### Port already in use

If you get "address already in use" errors, either:
1. Stop the conflicting service on your host
2. Change the port mapping in `docker-compose.yml`

### Database connection issues

1. Ensure `.env` variables match between services
2. Reset the database: `docker-compose down -v && docker-compose up`

### API not accessible from GUI

The nginx configuration proxies `/api` requests to the API container. Ensure:
1. Both containers are running: `docker-compose ps`
2. Check nginx logs: `docker-compose logs gui`

## Testing

The project includes a comprehensive test suite with pytest.

### Running Tests (Recommended)

The easiest way to run tests is using Task commands:

```bash
# Run all tests
go-task test-docker

# Or using the script directly
./run-tests.sh

# Run only unit tests
go-task test-docker-unit

# Run only integration tests
go-task test-docker-integration

# Run tests with coverage report
go-task test-docker-coverage

# Run specific test file
go-task test-docker-specific FILE=authentication/tests/unit/test_models.py

# Open test shell for debugging
go-task test-shell

# List all available tasks
go-task --list
```

### Running Tests Manually with Docker

```bash
# Build test container
go-task build-test

# Start database
go-task db-up

# Run tests
docker-compose --profile test run --rm api_test

# Run specific tests
docker-compose --profile test run --rm api_test pytest authentication/tests/unit/

# Run with markers
docker-compose --profile test run --rm api_test pytest -m "unit and auth"

# Stop containers
go-task down
```

### Test Organization

Tests are organized in the `digitalockbox_api/authentication/tests/` directory:

- `unit/` - Fast, isolated unit tests
- `integration/` - Integration tests with database
- `fixtures/` - Test data factories and fixtures
- `conftest.py` - Pytest configuration and shared fixtures

See [Testing Documentation](digitalockbox_api/authentication/tests/README.md) for detailed information.

### Available Task Commands

```bash
go-task --list                 # Show all available commands

# Testing
go-task test-docker            # Run all tests in Docker
go-task test-docker-unit       # Run unit tests
go-task test-docker-integration # Run integration tests
go-task test-docker-coverage   # Run with coverage
go-task test-all               # Run full test suite with database
go-task clean-test             # Clean test artifacts

# Database
go-task db-up                  # Start database
go-task db-down                # Stop database
go-task db-reset               # Reset database

# Services
go-task up                     # Start all services
go-task down                   # Stop all services
go-task build                  # Build all services
go-task logs SERVICE=api       # View logs for specific service

# Development
go-task shell                  # Open shell in API container
go-task migrate                # Run database migrations
go-task makemigrations         # Create new migrations
```

### Coverage Reports

After running tests with coverage, view the HTML report:

```bash
go-task coverage-report  # Opens in default browser (cross-platform)

# Or manually:
open digitalockbox_api/authentication/htmlcov/index.html  # macOS
xdg-open digitalockbox_api/authentication/htmlcov/index.html  # Linux
```

## License

MIT
