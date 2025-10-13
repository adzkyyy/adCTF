#!/bin/bash
# Environment switcher script for adCTF

case "$1" in
    "local")
        echo "🔄 Switching to LOCAL development environment..."
        cp .env.local .env
        echo "✅ Environment switched to LOCAL"
        echo "📝 Database will connect to: localhost:3306"
        echo "📝 Redis will connect to: localhost:6379"
        echo ""
        echo "You can now run:"
        echo "  python init_db.py"
        echo "  python run.py"
        ;;
    "docker")
        echo "🔄 Switching to DOCKER environment..."
        cp .env.docker .env
        echo "✅ Environment switched to DOCKER"
        echo "📝 Database will connect to: db:3306"
        echo "📝 Redis will connect to: redis:6379"
        echo ""
        echo "You can now run:"
        echo "  docker compose up -d"
        ;;
    *)
        echo "Usage: $0 {local|docker}"
        echo ""
        echo "Commands:"
        echo "  $0 local   - Switch to local development (connects to localhost)"
        echo "  $0 docker  - Switch to Docker environment (connects to service names)"
        echo ""
        echo "Current environment:"
        if grep -q "localhost" .env 2>/dev/null; then
            echo "  📍 LOCAL (connects to localhost)"
        elif grep -q "@db:" .env 2>/dev/null; then
            echo "  📍 DOCKER (connects to service names)"
        else
            echo "  ❓ UNKNOWN or no .env file found"
        fi
        exit 1
        ;;
esac