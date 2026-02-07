# Todo AI Chatbot

A full-stack todo application with AI chatbot integration, built with Next.js 15 and FastAPI.

## Architecture

- **Frontend**: Next.js 15 with Better Auth authentication
- **Backend**: FastAPI with Google Gemini AI integration
- **Database**: Neon PostgreSQL

## Local Development

### Prerequisites

- Node.js 20+
- Python 3.11+
- Docker Desktop
- Minikube (for Kubernetes deployment)
- Helm 3

### Running Locally

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

#### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

## Kubernetes Deployment (Minikube)

### Prerequisites

Ensure the following tools are installed:
- Docker Desktop
- Minikube
- kubectl
- Helm 3

### Quick Start

1. **Start Minikube**
   ```bash
   minikube start --driver=docker
   ```

2. **Build Docker Images**
   ```bash
   docker build -t todo-frontend:latest -f docker/frontend/Dockerfile frontend/
   docker build -t todo-backend:latest -f docker/backend/Dockerfile backend/
   ```

3. **Load Images into Minikube**
   ```bash
   minikube image load todo-frontend:latest
   minikube image load todo-backend:latest
   ```

4. **Configure Secrets**

   Update `helm/backend/values.yaml` and `helm/frontend/values.yaml` with your credentials:
   - `secrets.databaseUrl` - Neon PostgreSQL connection string
   - `secrets.betterAuthSecret` - JWT signing secret (min 32 chars)
   - `secrets.geminiApiKey` - Google Gemini API key (backend only)

5. **Deploy with Helm**
   ```bash
   helm install todo-backend helm/backend
   helm install todo-frontend helm/frontend
   ```

6. **Access the Application**
   ```bash
   minikube service todo-frontend --url
   ```

### Scaling

Scale replicas using Helm:
```bash
# Scale frontend to 3 replicas
helm upgrade todo-frontend helm/frontend --set replicaCount=3

# Scale backend to 2 replicas
helm upgrade todo-backend helm/backend --set replicaCount=2
```

### Useful Commands

```bash
# Check pod status
kubectl get pods

# Check services
kubectl get svc

# View logs
kubectl logs -l app=todo-frontend
kubectl logs -l app=todo-backend

# Uninstall
helm uninstall todo-frontend
helm uninstall todo-backend

# Stop Minikube
minikube stop
```

## Project Structure

```
.
├── frontend/          # Next.js frontend application
├── backend/           # FastAPI backend application
├── docker/            # Dockerfiles
│   ├── frontend/
│   └── backend/
├── helm/              # Helm charts
│   ├── frontend/
│   └── backend/
└── specs/             # Feature specifications
```

## Environment Variables

### Frontend
- `DATABASE_URL` - PostgreSQL connection string
- `BETTER_AUTH_SECRET` - JWT signing secret
- `NEXT_PUBLIC_API_URL` - Backend API URL

### Backend
- `DATABASE_URL` - PostgreSQL connection string
- `BETTER_AUTH_SECRET` - JWT verification secret
- `GOOGLE_API_KEY` - Gemini API key
- `FRONTEND_URL` - Frontend URL for CORS

## License

MIT
