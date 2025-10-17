# Docker Deployment Guide

Complete guide for running the Insurance Eligibility Agent using Docker and Docker Compose.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Usage](#usage)
- [Development Mode](#development-mode)
- [Troubleshooting](#troubleshooting)
- [Production Deployment](#production-deployment)

## Prerequisites

Before starting, ensure you have installed:

- **Docker**: Version 20.10 or higher
- **Docker Compose**: Version 2.0 or higher
- **Anthropic API Key**: Get one from [Anthropic Console](https://console.anthropic.com/)

Check your installations:

```bash
docker --version
docker-compose --version
```

## Quick Start

### 1. Clone and Navigate to Repository

```bash
cd eligibility-agent
```

### 2. Configure Environment Variables

Copy the example environment file and edit it with your settings:

```bash
cp .env.docker.example .env
```

Edit `.env` and add your Anthropic API key:

```env
ANTHROPIC_API_KEY=your_actual_api_key_here
POSTGRES_PASSWORD=your_secure_password
```

### 3. Build and Start Services

```bash
# Build the Docker image
docker-compose build

# Start all services (app + database)
docker-compose up -d
```

### 4. Verify Deployment

Check that all services are running:

```bash
docker-compose ps
```

Expected output:
```
NAME                      STATUS              PORTS
eligibility-agent-app     Up (healthy)        0.0.0.0:8000->8000/tcp
eligibility-agent-db      Up (healthy)        0.0.0.0:5432->5432/tcp
```

### 5. Access the Application

- **Web Interface**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Configuration

### Environment Variables

The application uses the following environment variables (defined in `.env`):

#### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `ANTHROPIC_API_KEY` | Your Anthropic API key | `sk-ant-...` |

#### Database Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `POSTGRES_USER` | Database username | `postgres` |
| `POSTGRES_PASSWORD` | Database password | `postgres` |
| `POSTGRES_DB` | Database name | `eligibility_agent` |
| `POSTGRES_PORT` | Database port | `5432` |

#### Application Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `APP_PORT` | Application port | `8000` |
| `LOG_LEVEL` | Logging level | `info` |
| `ENVIRONMENT` | Environment name | `production` |

## Usage

### Start Services

```bash
# Start all services in detached mode
docker-compose up -d

# Start and view logs
docker-compose up

# Start specific service
docker-compose up app
```

### Stop Services

```bash
# Stop all services (keeps data)
docker-compose stop

# Stop and remove containers (keeps data)
docker-compose down

# Stop and remove everything including volumes (⚠️ deletes data)
docker-compose down -v
```

### View Logs

```bash
# View logs from all services
docker-compose logs

# Follow logs in real-time
docker-compose logs -f

# View logs from specific service
docker-compose logs app
docker-compose logs postgres

# View last 100 lines
docker-compose logs --tail=100
```

### Restart Services

```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart app
```

### Execute Commands in Containers

```bash
# Access app container shell
docker-compose exec app bash

# Access PostgreSQL CLI
docker-compose exec postgres psql -U postgres -d eligibility_agent

# Run Python commands
docker-compose exec app python -c "print('Hello from Docker!')"
```

## Development Mode

For development with hot-reload functionality:

### 1. Edit docker-compose.yml

Uncomment the development sections in `docker-compose.yml`:

```yaml
app:
  # ... existing config ...

  # Uncomment these lines for development:
  volumes:
    - ./app:/app/app
    - ./static:/app/static
  command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Restart Services

```bash
docker-compose down
docker-compose up -d
```

Now code changes will automatically reload the application!

### 3. Debugging

View real-time logs while developing:

```bash
docker-compose logs -f app
```

## Troubleshooting

### Container Won't Start

**Check container status and logs:**

```bash
docker-compose ps
docker-compose logs app
```

**Common issues:**

1. **Port already in use**: Change `APP_PORT` in `.env`
2. **Missing API key**: Verify `ANTHROPIC_API_KEY` in `.env`
3. **Database connection**: Ensure PostgreSQL container is healthy

### Database Connection Issues

**Verify database is running:**

```bash
docker-compose exec postgres pg_isready -U postgres
```

**Reset database:**

```bash
docker-compose down -v  # ⚠️ This deletes all data
docker-compose up -d
```

### View Container Health

```bash
docker-compose ps
docker inspect eligibility-agent-app --format='{{.State.Health.Status}}'
```

### Rebuild Containers

If you made changes to the Dockerfile or requirements:

```bash
docker-compose build --no-cache
docker-compose up -d
```

### Clean Everything

Remove all containers, images, and volumes:

```bash
docker-compose down -v --rmi all
```

## Production Deployment

### Security Best Practices

1. **Use Strong Passwords**
   ```env
   POSTGRES_PASSWORD=$(openssl rand -base64 32)
   ```

2. **Don't Expose Database Port**

   Comment out in `docker-compose.yml`:
   ```yaml
   # ports:
   #   - "5432:5432"  # Remove this in production
   ```

3. **Use Secrets Management**

   Consider using Docker secrets or environment-specific secret managers:
   ```bash
   # AWS Secrets Manager
   # Azure Key Vault
   # Google Secret Manager
   ```

4. **Enable HTTPS**

   Use a reverse proxy like Nginx or Traefik with SSL certificates.

### Resource Limits

Add resource limits to `docker-compose.yml`:

```yaml
app:
  # ... existing config ...
  deploy:
    resources:
      limits:
        cpus: '1.0'
        memory: 1G
      reservations:
        cpus: '0.5'
        memory: 512M
```

### Monitoring

**Check resource usage:**

```bash
docker stats
```

**Health check endpoints:**

- Application: `http://localhost:8000/health`
- Database: `docker-compose exec postgres pg_isready`

### Backup Database

```bash
# Create backup
docker-compose exec postgres pg_dump -U postgres eligibility_agent > backup.sql

# Restore backup
docker-compose exec -T postgres psql -U postgres -d eligibility_agent < backup.sql
```

### Update Application

```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose build
docker-compose up -d
```

## Architecture

### Services Overview

```
┌─────────────────────────────────────────┐
│         eligibility-agent-app           │
│  (FastAPI + Claude AI Agent)            │
│  Port: 8000                             │
└──────────────┬──────────────────────────┘
               │
               │ Database Connection
               ↓
┌─────────────────────────────────────────┐
│         eligibility-agent-db            │
│  (PostgreSQL 15)                        │
│  Port: 5432                             │
│  Volume: postgres_data                  │
└─────────────────────────────────────────┘
```

### Network

Both services are connected via a dedicated Docker network (`eligibility-agent-network`), allowing secure internal communication.

### Volumes

- `postgres_data`: Persists database data across container restarts

## Additional Commands

### Check Disk Usage

```bash
docker system df
```

### Clean Up Unused Resources

```bash
docker system prune -a --volumes
```

### Export/Import Images

```bash
# Export image
docker save -o eligibility-agent.tar eligibility-agent-app

# Import image
docker load -i eligibility-agent.tar
```

## Support

For issues or questions:

1. Check application logs: `docker-compose logs app`
2. Verify environment variables: `docker-compose config`
3. Review health status: `docker-compose ps`
4. Check API documentation: http://localhost:8000/docs

---

**Happy Dockering!** 🐳
