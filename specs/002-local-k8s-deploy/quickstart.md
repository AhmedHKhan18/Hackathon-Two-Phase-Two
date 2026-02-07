# Quickstart: Local Kubernetes Deployment

**Feature**: 002-local-k8s-deploy
**Date**: 2026-01-27

## Prerequisites

Before starting, ensure you have:

- [ ] Docker Desktop installed and running
- [ ] Minikube installed (`minikube version`)
- [ ] kubectl installed (`kubectl version`)
- [ ] Helm 3 installed (`helm version`)
- [ ] Environment variables ready:
  - `DATABASE_URL` - Neon PostgreSQL connection string
  - `BETTER_AUTH_SECRET` - JWT signing secret (32+ characters)
  - `GEMINI_API_KEY` - Google Gemini API key

---

## Quick Deploy (5 Commands)

```bash
# 1. Start Minikube cluster
minikube start --driver=docker --cpus=2 --memory=4096

# 2. Build and load Docker images
docker build -t todo-frontend:latest -f docker/frontend/Dockerfile frontend/
docker build -t todo-backend:latest -f docker/backend/Dockerfile backend/
minikube image load todo-frontend:latest
minikube image load todo-backend:latest

# 3. Get Minikube IP and update values
MINIKUBE_IP=$(minikube ip)
echo "Minikube IP: $MINIKUBE_IP"

# 4. Deploy with Helm (update values first - see Configuration section)
helm install todo-backend helm/backend
helm install todo-frontend helm/frontend

# 5. Access the application
minikube service todo-frontend --url
```

---

## Detailed Steps

### Step 1: Start Minikube

```bash
# Start with recommended resources
minikube start --driver=docker --cpus=2 --memory=4096

# Verify cluster is running
minikube status
kubectl cluster-info
```

### Step 2: Build Docker Images

```bash
# Navigate to project root
cd /path/to/hackathon-two-phase-two

# Build frontend image
docker build -t todo-frontend:latest -f docker/frontend/Dockerfile frontend/

# Build backend image
docker build -t todo-backend:latest -f docker/backend/Dockerfile backend/

# Verify images exist
docker images | grep todo
```

### Step 3: Load Images into Minikube

```bash
# Load images (this may take a few minutes)
minikube image load todo-frontend:latest
minikube image load todo-backend:latest

# Verify images are loaded
minikube image ls | grep todo
```

### Step 4: Configure Environment

Get the Minikube IP:
```bash
MINIKUBE_IP=$(minikube ip)
echo "Minikube IP: $MINIKUBE_IP"
```

Update `helm/frontend/values.yaml`:
```yaml
config:
  nextPublicApiUrl: "http://<MINIKUBE_IP>:30000"

secrets:
  databaseUrl: "<YOUR_NEON_DATABASE_URL>"
  betterAuthSecret: "<YOUR_BETTER_AUTH_SECRET>"
```

Update `helm/backend/values.yaml`:
```yaml
config:
  frontendUrl: "http://<MINIKUBE_IP>:30080"

secrets:
  databaseUrl: "<YOUR_NEON_DATABASE_URL>"
  betterAuthSecret: "<YOUR_BETTER_AUTH_SECRET>"
  geminiApiKey: "<YOUR_GEMINI_API_KEY>"
```

### Step 5: Deploy with Helm

```bash
# Deploy backend first (frontend depends on it)
helm install todo-backend helm/backend

# Verify backend is running
kubectl get pods -l app=todo-backend
kubectl get svc todo-backend

# Deploy frontend
helm install todo-frontend helm/frontend

# Verify frontend is running
kubectl get pods -l app=todo-frontend
kubectl get svc todo-frontend
```

### Step 6: Access the Application

```bash
# Get service URL
minikube service todo-frontend --url

# Or access directly via Minikube IP
echo "Frontend: http://$MINIKUBE_IP:30080"
echo "Backend API: http://$MINIKUBE_IP:30000"
```

---

## Verification Commands

```bash
# Check all pods are running
kubectl get pods

# Check all services
kubectl get svc

# Check pod logs
kubectl logs -l app=todo-frontend
kubectl logs -l app=todo-backend

# Check pod events (for troubleshooting)
kubectl describe pod -l app=todo-frontend
kubectl describe pod -l app=todo-backend

# Test backend health endpoint
curl http://$MINIKUBE_IP:30000/
```

---

## Scaling

```bash
# Scale frontend to 3 replicas
helm upgrade todo-frontend helm/frontend --set replicaCount=3

# Verify scaling
kubectl get pods -l app=todo-frontend

# Scale backend to 2 replicas
helm upgrade todo-backend helm/backend --set replicaCount=2
```

---

## Cleanup

```bash
# Remove deployments
helm uninstall todo-frontend
helm uninstall todo-backend

# Stop Minikube (preserves state)
minikube stop

# Delete Minikube cluster (removes all data)
minikube delete
```

---

## Troubleshooting

### Pods stuck in Pending
```bash
kubectl describe pod <pod-name>
# Check for resource constraints or image pull issues
```

### ImagePullBackOff Error
```bash
# Ensure images are loaded into Minikube
minikube image ls | grep todo
# Re-load if missing
minikube image load todo-frontend:latest
```

### Pod CrashLoopBackOff
```bash
# Check pod logs
kubectl logs <pod-name> --previous
# Check environment variables are set correctly
kubectl describe pod <pod-name>
```

### Database Connection Issues
```bash
# Verify DATABASE_URL is correct
kubectl get secret todo-backend-secrets -o jsonpath='{.data.DATABASE_URL}' | base64 -d
# Ensure Neon database allows external connections
```

### Frontend Cannot Reach Backend
```bash
# Verify NEXT_PUBLIC_API_URL is set to correct Minikube IP
kubectl get configmap todo-frontend-config -o yaml
# Test backend directly
curl http://$MINIKUBE_IP:30000/
```

---

## Common Operations

### Update Configuration
```bash
# Edit values.yaml and upgrade
helm upgrade todo-backend helm/backend
helm upgrade todo-frontend helm/frontend
```

### View Logs
```bash
# Stream logs
kubectl logs -f -l app=todo-frontend
kubectl logs -f -l app=todo-backend
```

### Access Pod Shell
```bash
kubectl exec -it <pod-name> -- /bin/sh
```

### Restart Pods
```bash
kubectl rollout restart deployment/todo-frontend
kubectl rollout restart deployment/todo-backend
```
