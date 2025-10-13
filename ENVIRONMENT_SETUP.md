# Environment Configuration Guide

This project supports two different environment configurations:

## Files Created

- `.env.local` - For local development (connects to localhost)
- `.env.docker` - For Docker deployment (connects to service names)
- `switch-env.bat` - Windows script to switch environments
- `switch-env.sh` - Linux/Mac script to switch environments

## Usage

### For Local Development

1. Start the database services:
   ```bash
   docker compose -f docker-compose.db-only.yaml up -d
   ```

2. Switch to local environment:
   ```bash
   # Windows
   .\switch-env.bat local
   
   # Linux/Mac
   ./switch-env.sh local
   ```

3. Initialize the database:
   ```bash
   python init_db.py
   ```

4. Run the application:
   ```bash
   python run.py
   ```

### For Docker Deployment

1. Switch to Docker environment:
   ```bash
   # Windows
   .\switch-env.bat docker
   
   # Linux/Mac
   ./switch-env.sh docker
   ```

2. Run with Docker Compose:
   ```bash
   docker compose up -d
   ```

## Environment Differences

| Configuration | Database Host | Redis Host | Use Case |
|---------------|---------------|------------|----------|
| Local (.env.local) | localhost:3306 | localhost:6379 | Running Python directly on host |
| Docker (.env.docker) | db:3306 | redis:6379 | Running in Docker containers |

## Current Environment

To check which environment is currently active, run the switch script without arguments:

```bash
# Windows
.\switch-env.bat

# Linux/Mac
./switch-env.sh
```

This will show whether you're currently configured for LOCAL or DOCKER deployment.