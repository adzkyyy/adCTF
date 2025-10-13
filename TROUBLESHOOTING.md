# Docker Troubleshooting Guide

This guide helps resolve common Docker and database connection issues with adCTF.

## 🔍 Quick Diagnosis

Run these commands to diagnose issues:

```bash
# Check Docker status
docker info

# Check running containers
docker-compose ps

# Check container logs
docker-compose logs web
docker-compose logs db

# Check database health
docker-compose exec db mysql -u root -p -e "SHOW DATABASES;"
```

## 🚨 Common Issues & Solutions

### 1. "Database not ready" Error Loop

**Symptoms:**
```
⏳ Database not ready. Retrying in 2 seconds...
⏳ Database not ready. Retrying in 2 seconds...
```

**Solutions:**

#### A. Check Database Container Status
```bash
docker-compose logs db
```

Look for MySQL initialization messages. If you see errors about permissions or corrupt data:

```bash
# Stop containers and remove volumes
docker-compose down -v

# Remove all volumes
docker volume prune -f

# Restart
docker-compose up --build -d
```

#### B. Verify Environment Variables
Check your `.env` file contains:
```bash
MYSQL_ROOT_PASSWORD=your_password
MYSQL_DATABASE=adctf
MYSQL_USER=adctf_user  
MYSQL_PASSWORD=your_user_password
```

#### C. Wait Longer for MySQL Initialization
First-time MySQL container setup can take 2-3 minutes. Be patient.

### 2. Port Already in Use

**Symptoms:**
```
Error: Port 5000 is already in use
Error: Port 3306 is already in use
```

**Solutions:**

#### Check What's Using the Port
```bash
# On Linux/Mac
lsof -i :5000
lsof -i :3306

# On Windows
netstat -ano | findstr :5000
netstat -ano | findstr :3306
```

#### Change Ports in docker-compose.yaml
```yaml
services:
  web:
    ports:
      - "5001:5000"  # Use port 5001 instead
  db:
    ports:
      - "3307:3306"  # Use port 3307 instead
```

### 3. Permission Denied Errors

**Symptoms:**
```
Permission denied: '/var/lib/mysql'
Got permission denied while trying to connect
```

**Solutions:**

#### Fix Docker Volume Permissions
```bash
# Stop containers
docker-compose down

# Remove volumes
docker-compose down -v

# On Linux, fix permissions
sudo chown -R $USER:$USER .

# Restart
docker-compose up --build -d
```

### 4. Network Connection Issues

**Symptoms:**
```
Can't connect to MySQL server on 'db'
Name resolution failure
```

**Solutions:**

#### Recreate Docker Network
```bash
# Stop containers
docker-compose down

# Remove networks
docker network prune -f

# Restart
docker-compose up --build -d
```

### 5. Out of Disk Space

**Symptoms:**
```
No space left on device
Docker build failed
```

**Solutions:**

#### Clean Docker System
```bash
# Remove unused containers, networks, images
docker system prune -a

# Remove unused volumes
docker volume prune -f

# Check disk space
df -h
```

## 🔧 Advanced Troubleshooting

### Manual Database Connection Test

```bash
# Connect to running MySQL container
docker-compose exec db mysql -u root -p

# Test from web container
docker-compose exec web mysql -h db -u adctf_user -p
```

### Inspect Container Details

```bash
# Get detailed container info
docker-compose exec web env
docker inspect adctf_db_1

# Check container health
docker-compose exec db mysqladmin ping -h localhost -u root -p
```

### Debug Application Startup

```bash
# Run web container interactively
docker-compose run --rm web bash

# Manually run initialization
python init_db.py

# Check Python packages
pip list
```

## 📊 Monitoring Commands

### Real-time Logs
```bash
# Follow all logs
docker-compose logs -f

# Follow specific service
docker-compose logs -f web
docker-compose logs -f db
```

### Resource Usage
```bash
# Check container resource usage
docker stats

# Check system resources
df -h
free -h
```

### Container Health Checks
```bash
# Check all container health
docker-compose ps

# Manual health check
docker-compose exec db mysqladmin ping -h localhost -u root -p
docker-compose exec redis redis-cli ping
```

## 🆘 Emergency Reset

If all else fails, complete reset:

```bash
# 1. Stop everything
docker-compose down

# 2. Remove all containers
docker container prune -f

# 3. Remove all volumes
docker volume prune -f

# 4. Remove all networks
docker network prune -f

# 5. Remove all images (optional)
docker image prune -a -f

# 6. Clean build cache
docker builder prune -f

# 7. Restart Docker service
# On Linux:
sudo systemctl restart docker
# On Windows/Mac: Restart Docker Desktop

# 8. Fresh start
docker-compose up --build -d
```

## 📞 Getting Help

If you're still having issues:

1. **Collect logs:**
   ```bash
   docker-compose logs > debug.log
   ```

2. **Share system info:**
   ```bash
   docker version
   docker-compose version
   uname -a  # Linux/Mac
   systeminfo  # Windows
   ```

3. **Create an issue** on GitHub with:
   - Your OS and version
   - Docker and Docker Compose versions
   - Complete error logs
   - Your `.env` file (remove sensitive passwords)
   - Steps you've already tried

## 💡 Prevention Tips

1. **Regular cleanup:**
   ```bash
   docker system prune -f
   ```

2. **Monitor disk space:**
   ```bash
   df -h
   ```

3. **Keep Docker updated:**
   ```bash
   docker version
   ```

4. **Use setup scripts:**
   ```bash
   ./setup.sh  # Linux/Mac
   setup.bat   # Windows
   ```

---

*This troubleshooting guide covers the most common issues. For platform-specific problems, consult your OS documentation.*