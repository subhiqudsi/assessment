.PHONY: build logs run push build-frontend run-frontend install-frontend helm-apply helm-delete helm-upgrade help

# Default tag if not provided
TAG ?= latest

build:
	docker build -t backend ./backend

build-frontend:
	docker build -t frontend ./frontend

logs:
	docker-compose -f backend/docker-compose.yml logs -f

run:
	docker-compose -f backend/docker-compose.yml up -d

install-frontend:
	@echo "Installing frontend dependencies..."
	cd frontend && npm install

run-frontend:
	@echo "Starting frontend development server..."
	cd frontend && npm run dev

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
	@echo "  run               - Run backend with docker-compose"
	@echo "  install-frontend   - Install frontend dependencies"
	@echo "  run-frontend       - Run frontend development server locally"
	@echo "  push TAG=<tag>    - Push backend image with tag"
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