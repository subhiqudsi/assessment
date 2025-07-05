.PHONY: build logs run run-services run-web stop push build-frontend run-frontend install-frontend migrate make-migrations test populate-candidates populate-candidates-large clear-populate-candidates createsuperuser shell dbshell check collectstatic helm-apply helm-delete helm-upgrade help

# Default tag if not provided
TAG ?= latest
BACKEND_REPO ?= backend
FRONTEND_REPO ?= frontend


build:
	docker build -t backend -t $(BACKEND_REPO):$(TAG) ./backend

build-frontend:
	docker build -t frontend -t $(FRONTEND_REPO):$(TAG) ./frontend

logs:
	docker-compose -f backend/docker-compose.yml --env-file backend/.env logs -f

run:
	@echo "Starting supporting services (PostgreSQL, Elasticsearch)..."
	docker-compose -f backend/docker-compose.services.yml up -d
	@echo "Starting web application..."
	docker-compose -f backend/docker-compose.yml --env-file backend/.env up -d

run-services:
	@echo "Starting supporting services only (PostgreSQL, Elasticsearch)..."
	docker-compose -f backend/docker-compose.services.yml up -d

run-web:
	@echo "Starting web application only..."
	docker-compose -f backend/docker-compose.yml --env-file backend/.env up -d

stop:
	@echo "Stopping all services..."
	docker-compose -f backend/docker-compose.yml down
	docker-compose -f backend/docker-compose.services.yml down

install-frontend:
	@echo "Installing frontend dependencies..."
	cd frontend && npm install

run-frontend:
	@echo "Starting frontend development server..."
	cd frontend && npm run dev

make-migrations:
	@echo "Running django make migrations..."
	docker exec backend-web-1 python manage.py makemigrations
migrate:
	@echo "Running backend database migrations..."
	docker exec backend-web-1 python manage.py migrate

test:
	@echo "Running backend tests..."
	docker exec backend-web-1 python manage.py test

# Data management commands
populate-candidates:
	@echo "Populating database with test candidates..."
	docker exec backend-web-1 python manage.py populate_candidates --count 1000

populate-candidates-large:
	@echo "Populating database with large dataset..."
	docker exec backend-web-1 python manage.py populate_candidates --count 100000

clear-populate-candidates:
	@echo "Clearing and repopulating database with test candidates..."
	docker exec backend-web-1 python manage.py populate_candidates --clear

# Django admin commands
createsuperuser:
	@echo "Creating Django superuser..."
	docker exec -it backend-web-1 python manage.py createsuperuser

# Elasticsearch commands
init-elasticsearch:
	@echo "Initializing Elasticsearch index for Django logs..."
	docker exec backend-web-1 python manage.py init_elasticsearch

init-elasticsearch-force:
	@echo "Force recreating Elasticsearch index for Django logs..."
	docker exec backend-web-1 python manage.py init_elasticsearch --force

shell:
	@echo "Opening Django shell..."
	docker exec -it backend-web-1 python manage.py shell

dbshell:
	@echo "Opening database shell..."
	docker exec -it backend-web-1 python manage.py dbshell

# Development utilities
check:
	@echo "Running Django system checks..."
	docker exec backend-web-1 python manage.py check

collectstatic:
	@echo "Collecting static files..."
	docker exec backend-web-1 python manage.py collectstatic --noinput

push:
	@if [ -z "$(TAG)" ]; then \
		echo "Error: TAG is required. Usage: make push TAG=<tag>"; \
		exit 1; \
	fi
	docker tag backend:latest backend:$(TAG)
	docker push backend:$(TAG)

# Helm deployment commands
helm-apply:
	@echo "Deploying HR System with image tag: $(TAG)"
	helm upgrade --install hr-system ./helm/hr-system \
		--set backend.image.tag=$(TAG) \
		--set frontend.image.tag=$(TAG) \
		--wait --timeout=5m

helm-apply-backend:
	@echo "Deploying Backend with image tag: $(TAG)"
	helm upgrade --install hr-backend ./helm/backend \
		--set image.tag=$(TAG) \
		--wait --timeout=5m

helm-apply-frontend:
	@echo "Deploying Frontend with image tag: $(TAG)"
	helm upgrade --install hr-frontend ./helm/frontend \
		--set image.tag=$(TAG) \
		--wait --timeout=5m

helm-delete:
	@echo "Deleting HR System deployment"
	-helm uninstall hr-system
	-helm uninstall hr-backend
	-helm uninstall hr-frontend

helm-upgrade:
	@echo "Upgrading HR System with image tag: $(TAG)"
	helm upgrade hr-system ./helm/hr-system \
		--set backend.image.tag=$(TAG) \
		--set frontend.image.tag=$(TAG) \
		--wait --timeout=5m

helm-status:
	@echo "Checking Helm releases status"
	helm list
	@echo "\nKubernetes pods status:"
	kubectl get pods

helm-template:
	@echo "Rendering Helm templates with tag: $(TAG)"
	helm template hr-system ./helm/hr-system \
		--set backend.image.tag=$(TAG) \
		--set frontend.image.tag=$(TAG)

help:
	@echo "Available targets:"
	@echo "  build              - Build backend Docker image"
	@echo "  build-frontend     - Build frontend Docker image"
	@echo "  logs              - Show docker-compose logs"
	@echo "  run               - Run all services (PostgreSQL, Elasticsearch, Django)"
	@echo "  run-services       - Run supporting services only (PostgreSQL, Elasticsearch)"
	@echo "  run-web           - Run web application only (requires services to be running)"
	@echo "  stop              - Stop all running services"
	@echo "  install-frontend   - Install frontend dependencies"
	@echo "  run-frontend       - Run frontend development server locally"
	@echo "  make-migrations     - Run django makemigrations"
	@echo "  migrate           - Run backend database migrations"
	@echo "  test              - Run backend tests"
	@echo "  push TAG=<tag>    - Push backend image with tag"
	@echo ""
	@echo "Data Management Commands:"
	@echo "  populate-candidates       - Create 1,000 test candidates"
	@echo "  populate-candidates-large - Create 100,000 test candidates"
	@echo "  clear-populate-candidates - Clear and create 1,000 test candidates"
	@echo ""
	@echo "Django Admin Commands:"
	@echo "  createsuperuser    - Create Django superuser (interactive)"
	@echo "  shell             - Open Django shell (interactive)"
	@echo "  dbshell           - Open database shell (interactive)"
	@echo ""
	@echo "Development Utilities:"
	@echo "  check             - Run Django system checks"
	@echo "  collectstatic     - Collect static files"
	@echo ""
	@echo "Elasticsearch Commands:"
	@echo "  init-elasticsearch       - Initialize Elasticsearch index for logs"
	@echo "  init-elasticsearch-force - Force recreate Elasticsearch index"
	@echo ""
	@echo "Helm Commands:"
	@echo "  helm-apply [TAG=<tag>]        - Deploy complete HR system (default: latest)"
	@echo "  helm-apply-backend [TAG=<tag>] - Deploy backend only"
	@echo "  helm-apply-frontend [TAG=<tag>] - Deploy frontend only"
	@echo "  helm-upgrade [TAG=<tag>]      - Upgrade existing deployment"
	@echo "  helm-delete                   - Delete all deployments"
	@echo "  helm-status                   - Show deployment status"
	@echo "  helm-template [TAG=<tag>]     - Render templates without applying"
	@echo ""
	@echo "Examples:"
	@echo "  make helm-apply TAG=v1.0.0    - Deploy with specific image tag"
	@echo "  make helm-apply               - Deploy with latest tag"
	@echo "  make helm-upgrade TAG=v1.1.0  - Upgrade to new version"