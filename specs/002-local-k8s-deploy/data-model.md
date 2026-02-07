# Data Model: Kubernetes Resources

**Feature**: 002-local-k8s-deploy
**Date**: 2026-01-27
**Status**: Complete

## Overview

This document defines the Kubernetes resource model for deploying the Todo AI Chatbot to a local Minikube cluster.

---

## Resource Inventory

| Resource Type | Name | Namespace | Description |
|---------------|------|-----------|-------------|
| Deployment | todo-frontend | default | Frontend Next.js application |
| Deployment | todo-backend | default | Backend FastAPI application |
| Service | todo-frontend | default | NodePort service for frontend |
| Service | todo-backend | default | NodePort service for backend |
| ConfigMap | todo-frontend-config | default | Frontend environment configuration |
| ConfigMap | todo-backend-config | default | Backend environment configuration |
| Secret | todo-backend-secrets | default | Backend sensitive credentials |

---

## Frontend Resources

### Deployment: todo-frontend

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-frontend
  labels:
    app: todo-frontend
    tier: frontend
spec:
  replicas: 1  # Configurable via values.yaml
  selector:
    matchLabels:
      app: todo-frontend
  template:
    metadata:
      labels:
        app: todo-frontend
    spec:
      containers:
      - name: frontend
        image: todo-frontend:latest
        imagePullPolicy: Never  # Use local image
        ports:
        - containerPort: 3000
          name: http
        env:
        - name: NODE_ENV
          value: "production"
        envFrom:
        - configMapRef:
            name: todo-frontend-config
        - secretRef:
            name: todo-frontend-secrets
        resources:
          requests:
            cpu: "100m"
            memory: "128Mi"
          limits:
            cpu: "500m"
            memory: "512Mi"
        livenessProbe:
          httpGet:
            path: /
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 5
```

### Service: todo-frontend

```yaml
apiVersion: v1
kind: Service
metadata:
  name: todo-frontend
  labels:
    app: todo-frontend
spec:
  type: NodePort
  ports:
  - port: 3000
    targetPort: 3000
    nodePort: 30080  # Configurable
    name: http
  selector:
    app: todo-frontend
```

### ConfigMap: todo-frontend-config

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: todo-frontend-config
data:
  NEXT_PUBLIC_API_URL: "http://<minikube-ip>:30000"
```

### Secret: todo-frontend-secrets

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: todo-frontend-secrets
type: Opaque
stringData:
  DATABASE_URL: "<neon-connection-string>"
  BETTER_AUTH_SECRET: "<jwt-secret>"
```

---

## Backend Resources

### Deployment: todo-backend

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-backend
  labels:
    app: todo-backend
    tier: backend
spec:
  replicas: 1  # Configurable via values.yaml
  selector:
    matchLabels:
      app: todo-backend
  template:
    metadata:
      labels:
        app: todo-backend
    spec:
      containers:
      - name: backend
        image: todo-backend:latest
        imagePullPolicy: Never  # Use local image
        ports:
        - containerPort: 8000
          name: http
        envFrom:
        - configMapRef:
            name: todo-backend-config
        - secretRef:
            name: todo-backend-secrets
        resources:
          requests:
            cpu: "100m"
            memory: "128Mi"
          limits:
            cpu: "500m"
            memory: "512Mi"
        livenessProbe:
          httpGet:
            path: /
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

### Service: todo-backend

```yaml
apiVersion: v1
kind: Service
metadata:
  name: todo-backend
  labels:
    app: todo-backend
spec:
  type: NodePort
  ports:
  - port: 8000
    targetPort: 8000
    nodePort: 30000  # Configurable
    name: http
  selector:
    app: todo-backend
```

### ConfigMap: todo-backend-config

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: todo-backend-config
data:
  FRONTEND_URL: "http://<minikube-ip>:30080"
```

### Secret: todo-backend-secrets

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: todo-backend-secrets
type: Opaque
stringData:
  DATABASE_URL: "<neon-connection-string>"
  BETTER_AUTH_SECRET: "<jwt-secret>"
  GEMINI_API_KEY: "<gemini-api-key>"
```

---

## Resource Relationships

```
                           Deployment
                         todo-frontend
                               |
              +----------------+----------------+
              |                |                |
         ConfigMap          Secret          Service
    todo-frontend-config  todo-frontend-  todo-frontend
                              secrets      (NodePort:30080)
                               |                |
                               |                |
    Browser <------------------+----------------+
                               |
                               | NEXT_PUBLIC_API_URL
                               v
                           Deployment
                         todo-backend
                               |
              +----------------+----------------+
              |                |                |
         ConfigMap          Secret          Service
    todo-backend-config   todo-backend-   todo-backend
                             secrets      (NodePort:30000)
                               |
                               v
                    External Neon PostgreSQL
```

---

## Label Strategy

All resources use consistent labeling:

| Label | Purpose | Values |
|-------|---------|--------|
| `app` | Application identifier | `todo-frontend`, `todo-backend` |
| `tier` | Deployment tier | `frontend`, `backend` |
| `app.kubernetes.io/name` | Helm standard | Chart name |
| `app.kubernetes.io/instance` | Helm standard | Release name |
| `app.kubernetes.io/version` | Helm standard | App version |

---

## Resource Limits

| Resource | CPU Request | CPU Limit | Memory Request | Memory Limit |
|----------|-------------|-----------|----------------|--------------|
| Frontend | 100m | 500m | 128Mi | 512Mi |
| Backend | 100m | 500m | 128Mi | 512Mi |

These are conservative defaults suitable for local Minikube. Can be adjusted via Helm values.

---

## Port Assignments

| Service | Container Port | NodePort | Purpose |
|---------|----------------|----------|---------|
| Frontend | 3000 | 30080 | Browser access |
| Backend | 8000 | 30000 | API access |

NodePorts are in valid range (30000-32767) and non-conflicting.

---

## Validation Rules

1. **Image Availability**: Images must be loaded into Minikube before deployment
2. **Secret Population**: All secrets must have values before deployment
3. **ConfigMap URLs**: Must be updated with actual Minikube IP after cluster start
4. **Port Conflicts**: NodePorts must not conflict with other services
