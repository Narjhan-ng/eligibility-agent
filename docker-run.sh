#!/bin/bash
# ==============================================================================
# Docker Helper Script for Insurance Eligibility Agent
# ==============================================================================
# This script provides convenient commands to manage the Docker deployment
# ==============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "${BLUE}============================================================${NC}"
    echo -e "${BLUE}  Insurance Eligibility Agent - Docker Manager${NC}"
    echo -e "${BLUE}============================================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

check_env() {
    if [ ! -f .env ]; then
        print_warning ".env file not found!"
        echo ""
        echo "Creating .env from .env.docker.example..."
        cp .env.docker.example .env
        print_warning "Please edit .env and add your ANTHROPIC_API_KEY"
        echo ""
        echo "  nano .env"
        echo "  # or"
        echo "  vi .env"
        echo ""
        exit 1
    fi
}

check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        echo "Please install Docker: https://docs.docker.com/get-docker/"
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed"
        echo "Please install Docker Compose: https://docs.docker.com/compose/install/"
        exit 1
    fi
}

start() {
    print_header
    print_info "Starting services..."
    check_docker
    check_env

    docker-compose up -d

    echo ""
    print_success "Services started successfully!"
    echo ""
    print_info "Waiting for services to be healthy..."
    sleep 5

    docker-compose ps

    echo ""
    print_success "Application is running!"
    echo ""
    echo "  Web Interface:     http://localhost:8000"
    echo "  API Documentation: http://localhost:8000/docs"
    echo "  Health Check:      http://localhost:8000/health"
    echo ""
    print_info "View logs with: ./docker-run.sh logs"
}

stop() {
    print_header
    print_info "Stopping services..."
    docker-compose stop
    print_success "Services stopped"
}

restart() {
    print_header
    print_info "Restarting services..."
    docker-compose restart
    print_success "Services restarted"
}

logs() {
    print_header
    print_info "Showing logs (Ctrl+C to exit)..."
    docker-compose logs -f --tail=100
}

build() {
    print_header
    print_info "Building Docker images..."
    check_docker
    docker-compose build --no-cache
    print_success "Build completed"
}

clean() {
    print_header
    print_warning "This will remove all containers and images (data will be preserved)"
    read -p "Are you sure? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose down --rmi all
        print_success "Cleanup completed"
    else
        print_info "Cleanup cancelled"
    fi
}

clean_all() {
    print_header
    print_error "⚠️  WARNING: This will remove EVERYTHING including database data!"
    read -p "Are you sure? Type 'yes' to confirm: " -r
    echo
    if [[ $REPLY == "yes" ]]; then
        docker-compose down -v --rmi all
        print_success "Complete cleanup finished"
    else
        print_info "Cleanup cancelled"
    fi
}

status() {
    print_header
    print_info "Service Status:"
    docker-compose ps

    echo ""
    print_info "Resource Usage:"
    docker stats --no-stream $(docker-compose ps -q)
}

shell() {
    print_header
    print_info "Opening shell in app container..."
    docker-compose exec app bash
}

db_shell() {
    print_header
    print_info "Opening PostgreSQL shell..."
    docker-compose exec postgres psql -U postgres -d eligibility_agent
}

help() {
    print_header
    echo ""
    echo "Usage: ./docker-run.sh [command]"
    echo ""
    echo "Commands:"
    echo "  start       Start all services (build if needed)"
    echo "  stop        Stop all services"
    echo "  restart     Restart all services"
    echo "  logs        View logs (follow mode)"
    echo "  build       Rebuild Docker images"
    echo "  status      Show service status and resource usage"
    echo "  shell       Open bash shell in app container"
    echo "  db-shell    Open PostgreSQL shell"
    echo "  clean       Remove containers and images (keep data)"
    echo "  clean-all   Remove EVERYTHING including data (⚠️  dangerous)"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./docker-run.sh start       # Start the application"
    echo "  ./docker-run.sh logs        # View logs"
    echo "  ./docker-run.sh status      # Check status"
    echo ""
}

# Main script
case "${1:-help}" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    logs)
        logs
        ;;
    build)
        build
        ;;
    status)
        status
        ;;
    shell)
        shell
        ;;
    db-shell)
        db_shell
        ;;
    clean)
        clean
        ;;
    clean-all)
        clean_all
        ;;
    help|*)
        help
        ;;
esac
