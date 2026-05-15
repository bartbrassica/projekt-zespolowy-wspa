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

### 3. Run with Docker Compose

Build and start all services:

```bash
docker-compose up --build
```

Or run in detached mode:

```bash
docker-compose up -d --build
```

### 4. Access the application

- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/docs
- **Database**: localhost:5433 (PostgreSQL)

## Development

### View logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f gui
docker-compose logs -f db
```

### Stop services

```bash
docker-compose down
```

### Reset database

To completely reset the database (removes all data):

```bash
docker-compose down -v
docker-compose up
```

### Rebuild specific service

```bash
docker-compose up -d --build api
docker-compose up -d --build gui
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

## License

MIT
