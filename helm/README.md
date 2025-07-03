# HR System Helm Charts

This directory contains Helm charts for deploying the HR System to Kubernetes.

## Structure

```
helm/
├── backend/              # Django backend chart
├── frontend/             # Next.js frontend chart
├── hr-system/           # Umbrella chart for complete system
└── README.md
```

## Prerequisites

- Kubernetes cluster
- Helm 3.x installed
- NGINX Ingress Controller (for ingress)

## Quick Start

### Deploy the complete system

```bash
# From the helm directory
helm install hr-system ./hr-system
```

### Deploy individual components

```bash
# Backend only
helm install hr-backend ./backend

# Frontend only
helm install hr-frontend ./frontend
```

## Configuration

### Backend Configuration

Key values in `backend/values.yaml`:

- `image.repository`: Backend Docker image
- `database.type`: Database type (sqlite3 or postgresql)
- `storage.type`: Storage type (local or s3)
- `ingress.hosts`: Backend hostname

### Frontend Configuration

Key values in `frontend/values.yaml`:

- `image.repository`: Frontend Docker image
- `env.NEXT_PUBLIC_API_URL`: Backend API URL
- `ingress.hosts`: Frontend hostname

### Umbrella Chart Configuration

The `hr-system` chart deploys both components with coordinated configuration:

```yaml
backend:
  enabled: true
  # backend overrides
  
frontend:
  enabled: true
  # frontend overrides
```

## Deployment Examples

### Development Environment

```bash
# Deploy with development values
helm install hr-system ./hr-system \
  --set backend.env[0].value="True" \
  --set frontend.env[0].value="development"
```

### Production Environment

```bash
# Deploy with production values
helm install hr-system ./hr-system \
  --set backend.database.type="postgresql" \
  --set backend.database.host="postgres.example.com" \
  --set backend.storage.type="s3" \
  --set frontend.env[0].value="production"
```

### Custom Domain

```bash
# Deploy with custom domain
helm install hr-system ./hr-system \
  --set global.domain="mycompany.com" \
  --set backend.ingress.hosts[0].host="api.mycompany.com" \
  --set frontend.ingress.hosts[0].host="hr.mycompany.com"
```

## Accessing the Application

After deployment, add entries to your `/etc/hosts` file:

```
<INGRESS_IP> hr-system.local
<INGRESS_IP> api.hr-system.local
```

Or configure your DNS to point the domains to your ingress controller.

## Scaling

### Manual Scaling

```bash
# Scale backend
kubectl scale deployment hr-backend --replicas=3

# Scale frontend
kubectl scale deployment hr-frontend --replicas=3
```

### Auto Scaling

Enable HPA in values:

```yaml
autoscaling:
  enabled: true
  minReplicas: 1
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80
```

## Storage

### Backend Storage

For production, configure persistent storage:

```yaml
backend:
  storage:
    type: s3
    # Add S3 configuration
```

### Database

For production, use external database:

```yaml
backend:
  database:
    type: postgresql
    host: postgres.example.com
    port: 5432
    name: hr_system
    user: hr_user
    password: "secure_password"
```

## Monitoring and Logging

### Health Checks

Both charts include health check probes:
- Liveness probe: `/api/health/` (backend), `/` (frontend)
- Readiness probe: Same as liveness

### Logging

Configure centralized logging:

```yaml
backend:
  logging:
    elasticsearch:
      enabled: true
      host: elasticsearch.example.com
      port: 9200
```

## Troubleshooting

### Check pod status

```bash
kubectl get pods
kubectl describe pod <pod-name>
```

### Check logs

```bash
kubectl logs <pod-name>
```

### Check ingress

```bash
kubectl get ingress
kubectl describe ingress <ingress-name>
```

### Check services

```bash
kubectl get services
```

## Uninstalling

```bash
# Remove complete system
helm uninstall hr-system

# Remove individual components
helm uninstall hr-backend
helm uninstall hr-frontend
```

## Development

### Testing Charts

```bash
# Lint charts
helm lint ./backend
helm lint ./frontend
helm lint ./hr-system

# Dry run
helm install hr-system ./hr-system --dry-run --debug

# Template rendering
helm template hr-system ./hr-system
```

### Updating Dependencies

```bash
# Update umbrella chart dependencies
cd hr-system
helm dependency update
```