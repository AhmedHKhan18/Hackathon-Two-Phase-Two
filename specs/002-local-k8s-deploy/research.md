# Research: Local Kubernetes Deployment

**Feature**: 002-local-k8s-deploy
**Date**: 2026-01-27
**Status**: Complete

## Research Summary

This document consolidates research findings for deploying the Todo AI Chatbot to a local Minikube Kubernetes cluster.

---

## 1. Docker Best Practices for Next.js 15

### Decision: Multi-stage build with standalone output

### Rationale:
- Next.js 15 supports `output: 'standalone'` which creates a minimal production bundle
- Multi-stage builds reduce final image size by excluding dev dependencies and build artifacts
- Alpine-based runner image provides smallest footprint (~150MB vs ~1GB)

### Alternatives Considered:
1. **Single-stage build** - Rejected: Includes node_modules, resulting in ~1GB+ images
2. **Distroless images** - Rejected: More complex debugging, limited tooling
3. **Standard Node image** - Rejected: ~300MB larger than Alpine variant

### Implementation Pattern:
```dockerfile
# Stage 1: Dependencies
FROM node:20-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

# Stage 2: Builder
FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# Stage 3: Runner
FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public
EXPOSE 3000
CMD ["node", "server.js"]
```

### Required Config Change:
Add to `next.config.ts`:
```typescript
output: 'standalone'
```

---

## 2. Docker Best Practices for FastAPI/Python

### Decision: Single-stage slim build with pip cache

### Rationale:
- Python applications have simpler build process than Node.js
- `python:3.11-slim` provides good balance of size (~150MB) and compatibility
- pip caching layer reduces rebuild time

### Alternatives Considered:
1. **Alpine Python** - Rejected: Requires compilation of C extensions (psycopg2), slower builds
2. **Multi-stage** - Rejected: Minimal benefit for Python; single stage sufficient
3. **Distroless Python** - Rejected: Debugging limitations

### Implementation Pattern:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 3. Minikube Local Image Loading

### Decision: Use `minikube image load` command

### Rationale:
- Simplest approach for local development
- No registry setup required
- Works with standard Docker Desktop installation
- Images persist across Minikube restarts

### Alternatives Considered:
1. **Minikube Docker daemon (`eval $(minikube docker-env)`)** - Rejected: Requires building inside Minikube context, complicates workflow
2. **Local registry** - Rejected: Additional infrastructure, overkill for local dev
3. **Kind load** - N/A: Using Minikube, not Kind

### Implementation Pattern:
```bash
# Build images locally
docker build -t todo-frontend:latest -f docker/frontend/Dockerfile frontend/
docker build -t todo-backend:latest -f docker/backend/Dockerfile backend/

# Load into Minikube
minikube image load todo-frontend:latest
minikube image load todo-backend:latest
```

### Important Configuration:
Set `imagePullPolicy: Never` in Kubernetes manifests to use local images:
```yaml
spec:
  containers:
  - name: frontend
    image: todo-frontend:latest
    imagePullPolicy: Never
```

---

## 4. Helm Chart Patterns for Web Apps

### Decision: Separate charts per service with shared values pattern

### Rationale:
- Independent deployment and scaling of frontend/backend
- Clear separation of concerns
- Follows Helm best practices for microservices

### Alternatives Considered:
1. **Umbrella chart** - Rejected: Added complexity for 2 services
2. **Raw manifests** - Rejected: Spec requires Helm charts (FR-003, FR-004)
3. **Kustomize** - Rejected: Helm specified in requirements

### Chart Structure:
```
helm/
├── frontend/
│   ├── Chart.yaml           # Chart metadata
│   ├── values.yaml          # Default configuration
│   └── templates/
│       ├── _helpers.tpl     # Template helpers
│       ├── deployment.yaml  # Deployment resource
│       ├── service.yaml     # Service resource
│       └── configmap.yaml   # Environment config
└── backend/
    ├── Chart.yaml
    ├── values.yaml
    └── templates/
        ├── _helpers.tpl
        ├── deployment.yaml
        ├── service.yaml
        ├── configmap.yaml
        └── secret.yaml      # Sensitive env vars
```

### Service Types:
- Frontend: `NodePort` (external browser access)
- Backend: `NodePort` (API access from frontend via Minikube IP)

---

## 5. Environment Variable Handling in K8s

### Decision: ConfigMaps for non-sensitive, Secrets for sensitive data

### Rationale:
- Kubernetes best practice separation
- Secrets are base64 encoded (not encrypted, but standard practice)
- ConfigMaps allow easy updates without redeployment

### Variable Classification:

| Variable | Resource Type | Notes |
|----------|---------------|-------|
| DATABASE_URL | Secret | Contains credentials |
| BETTER_AUTH_SECRET | Secret | JWT signing key |
| GEMINI_API_KEY | Secret | API key |
| NEXT_PUBLIC_API_URL | ConfigMap | Public URL, no secret |
| FRONTEND_URL | ConfigMap | CORS configuration |
| NODE_ENV | Inline env | Static value |

### Alternatives Considered:
1. **All inline env vars** - Rejected: No separation, harder to manage
2. **External secrets operator** - Rejected: Overkill for local dev
3. **HashiCorp Vault** - Rejected: Not needed for local Minikube

### Implementation Pattern:
```yaml
# secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: {{ .Release.Name }}-secrets
type: Opaque
stringData:
  DATABASE_URL: {{ .Values.secrets.databaseUrl | quote }}
  BETTER_AUTH_SECRET: {{ .Values.secrets.betterAuthSecret | quote }}
```

```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ .Release.Name }}-config
data:
  FRONTEND_URL: {{ .Values.config.frontendUrl | quote }}
```

---

## 6. Tool Availability Research

### Docker Desktop
- **Required Version**: 4.0+ (Docker Engine 20.10+)
- **Gordon AI Agent**: Available in Docker Desktop 4.53+, optional enhancement
- **Fallback**: Standard Docker CLI sufficient for all operations

### Minikube
- **Required Version**: 1.30+ (Kubernetes 1.28+)
- **Driver**: Docker (default on Windows)
- **Resources**: Minimum 2 CPU, 4GB RAM recommended

### kubectl
- **Required Version**: 1.28+ (matching Minikube K8s version)
- **Installation**: Via Minikube (`minikube kubectl`) or standalone

### Helm
- **Required Version**: 3.12+
- **Installation**: Via Chocolatey, Scoop, or direct download

### kubectl-ai (Optional)
- **Purpose**: AI-assisted kubectl commands
- **Fallback**: Claude Code generates kubectl commands directly

### kagent (Optional)
- **Purpose**: Kubernetes agent for debugging
- **Fallback**: Standard kubectl commands

---

## Conclusions

All research tasks are complete. Key decisions:

1. **Frontend Docker**: Multi-stage Alpine build with standalone output
2. **Backend Docker**: Single-stage slim build
3. **Image Loading**: `minikube image load` with `imagePullPolicy: Never`
4. **Helm Strategy**: Separate charts per service
5. **Env Vars**: ConfigMaps + Secrets separation

No NEEDS CLARIFICATION items remain. Ready for Phase 1 design artifacts.
