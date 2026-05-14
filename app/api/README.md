# Digital Lockbox - API

A secure password management REST API built with Django and Django Ninja, featuring JWT authentication, end-to-end encryption, and comprehensive password management.

## Tech Stack

- **Framework**: Django with Django Ninja REST framework
- **Language**: Python 3.12.9
- **Database**: PostgreSQL
- **Authentication**: JWT (ES512 algorithm)
- **Password Hashing**: Argon2
- **Encryption**: AES-256-GCM with client-side encryption
- **Package Manager**: uv

## Features

- User registration and authentication
- Email verification
- Password reset functionality
- Secure password storage with client-side encryption
- Password sharing between users
- Password expiration management
- JWT token-based authentication
- Rate limiting and security best practices

## Prerequisites

- Python 3.12.9+
- PostgreSQL 16+
- uv (recommended) or pip

## Development Setup

### 1. Install dependencies

Using uv (recommended):

```bash
uv sync
```

Using pip:

```bash
pip install -r requirements.txt
```

### 2. Configure environment variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Database Configuration
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=localhost
DB_PORT=5432

# Django Configuration
CLIENT_SECRET=your-very-secure-secret-key-here
DEBUG=True
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
FRONTEND_URL=http://localhost:5173
```

**Important**:
- Generate a strong `CLIENT_SECRET` for production
- Use Gmail App Password for `EMAIL_HOST_PASSWORD`
- Set `DEBUG=False` in production
- `JWT_ALG=ES512` uses elliptic curve cryptography for tokens

### 3. Set up the database

Create a PostgreSQL database:

```bash
psql -U postgres
CREATE DATABASE your_database_name;
CREATE USER your_database_user WITH PASSWORD 'your_database_password';
GRANT ALL PRIVILEGES ON DATABASE your_database_name TO your_database_user;
\q
```

### 4. Run migrations

```bash
uv run python authentication/manage.py migrate
```

### 5. Create a superuser (optional)

```bash
uv run python authentication/manage.py createsuperuser
```

### 6. Start development server

```bash
uv run python authentication/manage.py runserver
```

The API will be available at `http://localhost:8000`

## Available Commands

- `uv run python authentication/manage.py runserver` - Start development server
- `uv run python authentication/manage.py migrate` - Run database migrations
- `uv run python authentication/manage.py makemigrations` - Create new migrations
- `uv run python authentication/manage.py createsuperuser` - Create admin user
- `uv run python authentication/manage.py test` - Run tests
- `ruff check .` - Run linter

## Project Structure

```
digitalockbox_api/
    authentication/          # Main Django app
        authentication/      # Core application
            endpoints.py              # Auth endpoints (login, register, etc.)
            password_endpoints.py     # Password management endpoints
            models.py                 # Database models
            schemas.py                # Pydantic schemas for validation
            encryption_service.py     # Encryption utilities
            email_service.py          # Email sending service
            db_utils.py               # Database helper functions
            password_expiration_manager.py  # Password expiry logic
            settings.py               # Django settings
            urls.py                   # URL routing
        management/          # Custom management commands
        migrations/          # Database migrations
        templates/           # Email templates
    manage.py            # Django management script
    keys/                    # JWT signing keys (ES512)
    pyproject.toml          # Python dependencies
    uv.lock                 # Locked dependencies
    Dockerfile              # Docker image definition
    README.md               # This file
```

## API Documentation

Once the server is running, visit:

- **Interactive API Docs**: http://localhost:8000/api/docs
- **OpenAPI Schema**: http://localhost:8000/api/openapi.json

## Key Endpoints

### Authentication

- `POST /api/register` - Register new user
- `POST /api/login` - Login and receive JWT tokens
- `POST /api/refresh` - Refresh access token
- `POST /api/logout` - Logout (invalidate refresh token)
- `GET /api/verify-email/{token}` - Verify email address
- `POST /api/forgot-password` - Request password reset
- `POST /api/reset-password` - Reset password with token

### Password Management

- `POST /api/passwords` - Store new password
- `GET /api/passwords` - List user's passwords
- `GET /api/passwords/{id}` - Get specific password
- `PUT /api/passwords/{id}` - Update password
- `DELETE /api/passwords/{id}` - Delete password
- `POST /api/passwords/share` - Share password with another user
- `GET /api/passwords/shared` - Get shared passwords

### User Management

- `GET /api/user` - Get current user info
- `PUT /api/user` - Update user info
- `POST /api/change-password` - Change user password

## Security Features

### Encryption

- Client-side encryption using AES-256-GCM
- Passwords are encrypted before being sent to the server
- Server stores only encrypted data
- Encryption keys derived from user's master password

### Authentication

- JWT tokens with ES512 (Elliptic Curve) signing
- Access tokens (short-lived) + Refresh tokens (long-lived)
- Secure token storage and validation
- Password reset tokens with expiration

### Password Security

- Argon2 password hashing
- Password expiration management
- Secure password sharing between users
- Rate limiting on authentication endpoints

## Docker Deployment

### Build and run

```bash
docker build -t digitalockbox-api .
docker run -p 8000:8000 --env-file .env digitalockbox-api
```

### Using Docker Compose

See the main project README for full Docker Compose setup.

## Environment-Specific Configuration

### Development

```env
DEBUG=True
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
FRONTEND_URL=http://localhost:5173
```

### Production

```env
DEBUG=False
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
FRONTEND_URL=https://yourdomain.com
```

## Database Migrations

### Create new migration

```bash
uv run python authentication/manage.py makemigrations
```

### Apply migrations

```bash
uv run python authentication/manage.py migrate
```

### Rollback migration

```bash
uv run python authentication/manage.py migrate authentication <migration_name>
```

## Testing

Run tests:

```bash
uv run python authentication/manage.py test
```

## Troubleshooting

### Database connection errors

1. Verify PostgreSQL is running
2. Check `.env` database credentials
3. Ensure database exists: `psql -U postgres -l`

### Email not sending

1. For Gmail, use App Password, not regular password
2. Set `EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend` for development
3. Check email credentials in `.env`

### JWT token errors

1. Ensure `keys/` directory exists with ES512 key pair
2. Verify `JWT_ALG=ES512` in `.env`
3. Check token expiration settings

## Contributing

1. Follow PEP 8 style guide
2. Run `ruff check .` before committing
3. Write tests for new features
4. Update API documentation

## License

MIT
