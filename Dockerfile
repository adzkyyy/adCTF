# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    build-essential \
    default-mysql-client \
    --no-install-recommends && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed Python packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Create a wait script for database readiness
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
echo "🔄 Waiting for MySQL database to be ready..."\n\
echo "Database details: ${DB_HOST}:${DB_PORT} with user ${DB_USER}"\n\
\n\
# Wait for MySQL port to be available\n\
echo "⏳ Checking if database port is accessible..."\n\
timeout=60\n\
counter=0\n\
until nc -z "$DB_HOST" "$DB_PORT" 2>/dev/null; do\n\
  if [ $counter -ge $timeout ]; then\n\
    echo "❌ Timeout waiting for database port to be available"\n\
    exit 1\n\
  fi\n\
  echo "⏳ Database port not ready. Retrying in 2 seconds... ($counter/$timeout)"\n\
  sleep 2\n\
  counter=$((counter+2))\n\
done\n\
echo "✅ Database port is accessible!"\n\
\n\
# Wait for MySQL to accept connections\n\
echo "⏳ Checking if database accepts connections..."\n\
counter=0\n\
until mysql -h"$DB_HOST" -P"$DB_PORT" -u"$DB_USER" -p"$DB_PASSWORD" --skip-ssl -e "SELECT 1" "$DB_NAME" >/dev/null 2>&1; do\n\
  if [ $counter -ge $timeout ]; then\n\
    echo "❌ Timeout waiting for database to accept connections"\n\
    echo "❌ Check database credentials and permissions"\n\
    exit 1\n\
  fi\n\
  echo "⏳ Database not ready. Retrying in 2 seconds... ($counter/$timeout)"\n\
  sleep 2\n\
  counter=$((counter+2))\n\
done\n\
echo "✅ Database is ready and accepting connections!"\n\
\n\
# Initialize database\n\
echo "🔄 Initializing database..."\n\
python init_db.py\n\
\n\
# Start the application\n\
echo "🚀 Starting Flask application..."\n\
exec python run.py\n\
' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Install netcat for port checking
RUN apt-get update && apt-get install -y netcat-openbsd && rm -rf /var/lib/apt/lists/*

# Run the entrypoint script
CMD ["/app/entrypoint.sh"]
