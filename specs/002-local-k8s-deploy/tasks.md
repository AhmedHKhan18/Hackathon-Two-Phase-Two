# Tasks: Local Kubernetes Deployment

**Input**: Design documents from `/specs/002-local-k8s-deploy/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Not explicitly requested. Validation is via `helm lint`, `kubectl get pods`, and manual E2E testing per spec.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing. Note: For this infrastructure feature, User Stories 2 and 5 (Container Images, AI-Assisted Generation) are prerequisites that feed into User Stories 1, 3, and 4.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

Infrastructure artifacts at repository root:
- **Dockerfiles**: `docker/frontend/Dockerfile`, `docker/backend/Dockerfile`
- **Helm Charts**: `helm/frontend/`, `helm/backend/`
- **Application code**: `frontend/`, `backend/` (existing, mostly unchanged)

---

## Phase 1: Setup (Environment Preparation)

**Purpose**: Verify tools and create project structure for infrastructure artifacts

- [x] T001 Verify Docker Desktop installation and version (run `docker --version`)
- [x] T002 Verify or install Minikube (run `minikube version`)
- [x] T003 Verify or install kubectl (run `kubectl version --client`)
- [x] T004 Verify or install Helm 3 (run `helm version`)
- [x] T005 Create docker/ directory structure at repository root
- [x] T006 Create helm/ directory structure at repository root
- [x] T007 Start Minikube cluster with Docker driver (run `minikube start --driver=docker --cpus=2 --memory=4096`)
- [x] T008 Verify Minikube cluster is running (run `minikube status` and `kubectl cluster-info`)

**Checkpoint**: Environment ready - all tools verified and Minikube cluster running

---

## Phase 2: Foundational (Next.js Config Update)

**Purpose**: Required application config change before containerization

**CRITICAL**: This must complete before container images can be built

- [x] T009 Add `output: 'standalone'` to frontend/next.config.ts for Docker compatibility

**Checkpoint**: Foundation ready - application configured for containerization

---

## Phase 3: User Story 2 - Build Container Images (Priority: P1)

**Goal**: Containerize frontend and backend applications using Docker

**Independent Test**: Run `docker images | grep todo` to verify both images exist, then run each container locally to verify startup

### Implementation for User Story 2

- [x] T010 [P] [US2] Generate frontend Dockerfile using AI (Claude Code) in docker/frontend/Dockerfile
- [x] T011 [P] [US2] Generate backend Dockerfile using AI (Claude Code) in docker/backend/Dockerfile
- [x] T012 [US2] Build frontend Docker image (run `docker build -t todo-frontend:latest -f docker/frontend/Dockerfile frontend/`)
- [x] T013 [US2] Build backend Docker image (run `docker build -t todo-backend:latest -f docker/backend/Dockerfile backend/`)
- [x] T014 [P] [US2] Test frontend container locally (run `docker run --rm -p 3000:3000 todo-frontend:latest`)
- [x] T015 [P] [US2] Test backend container locally (run `docker run --rm -p 8000:8000 -e DATABASE_URL=... todo-backend:latest`)
- [x] T016 [US2] Load frontend image into Minikube (run `minikube image load todo-frontend:latest`)
- [x] T017 [US2] Load backend image into Minikube (run `minikube image load todo-backend:latest`)
- [x] T018 [US2] Verify images loaded in Minikube (run `minikube image ls | grep todo`)

**Checkpoint**: Container images built, tested, and loaded into Minikube

---

## Phase 4: User Story 3 - Package Application with Helm Charts (Priority: P2)

**Goal**: Create Helm charts for declarative deployment management

**Independent Test**: Run `helm lint helm/frontend` and `helm lint helm/backend` - both should pass with zero errors

### Implementation for User Story 3

- [x] T019 [P] [US3] Generate frontend Helm Chart.yaml using AI in helm/frontend/Chart.yaml
- [x] T020 [P] [US3] Generate backend Helm Chart.yaml using AI in helm/backend/Chart.yaml
- [x] T021 [P] [US3] Generate frontend values.yaml using AI in helm/frontend/values.yaml
- [x] T022 [P] [US3] Generate backend values.yaml using AI in helm/backend/values.yaml
- [x] T023 [P] [US3] Generate frontend _helpers.tpl using AI in helm/frontend/templates/_helpers.tpl
- [x] T024 [P] [US3] Generate backend _helpers.tpl using AI in helm/backend/templates/_helpers.tpl
- [x] T025 [P] [US3] Generate frontend deployment.yaml using AI in helm/frontend/templates/deployment.yaml
- [x] T026 [P] [US3] Generate backend deployment.yaml using AI in helm/backend/templates/deployment.yaml
- [x] T027 [P] [US3] Generate frontend service.yaml using AI in helm/frontend/templates/service.yaml
- [x] T028 [P] [US3] Generate backend service.yaml using AI in helm/backend/templates/service.yaml
- [x] T029 [P] [US3] Generate frontend configmap.yaml using AI in helm/frontend/templates/configmap.yaml
- [x] T030 [P] [US3] Generate backend configmap.yaml using AI in helm/backend/templates/configmap.yaml
- [x] T031 [P] [US3] Generate frontend secret.yaml using AI in helm/frontend/templates/secret.yaml
- [x] T032 [P] [US3] Generate backend secret.yaml using AI in helm/backend/templates/secret.yaml
- [x] T033 [US3] Validate frontend Helm chart (run `helm lint helm/frontend`)
- [x] T034 [US3] Validate backend Helm chart (run `helm lint helm/backend`)
- [x] T035 [US3] Test frontend template rendering (run `helm template todo-frontend helm/frontend`)
- [x] T036 [US3] Test backend template rendering (run `helm template todo-backend helm/backend`)

**Checkpoint**: Helm charts complete and validated - ready for deployment

---

## Phase 5: User Story 1 - Deploy Application to Local Kubernetes (Priority: P1)

**Goal**: Deploy complete Todo AI Chatbot to Minikube with both pods running

**Independent Test**: Run `kubectl get pods` - both frontend and backend pods should show Running status

### Implementation for User Story 1

- [x] T037 [US1] Get Minikube IP for configuration (run `minikube ip`)
- [x] T038 [US1] Update helm/frontend/values.yaml with Minikube IP for NEXT_PUBLIC_API_URL
- [x] T039 [US1] Update helm/backend/values.yaml with Minikube IP for FRONTEND_URL
- [x] T040 [US1] Update helm/frontend/values.yaml with secrets (DATABASE_URL, BETTER_AUTH_SECRET)
- [x] T041 [US1] Update helm/backend/values.yaml with secrets (DATABASE_URL, BETTER_AUTH_SECRET, GEMINI_API_KEY)
- [x] T042 [US1] Deploy backend Helm chart (run `helm install todo-backend helm/backend`)
- [x] T043 [US1] Verify backend pod is running (run `kubectl get pods -l app=todo-backend`)
- [x] T044 [US1] Verify backend service is created (run `kubectl get svc todo-backend`)
- [x] T045 [US1] Deploy frontend Helm chart (run `helm install todo-frontend helm/frontend`)
- [x] T046 [US1] Verify frontend pod is running (run `kubectl get pods -l app=todo-frontend`)
- [x] T047 [US1] Verify frontend service is created (run `kubectl get svc todo-frontend`)
- [x] T048 [US1] Get frontend service URL (run `minikube service todo-frontend --url`)
- [ ] T049 [US1] Verify frontend loads in browser (access URL from T048) - MANUAL TEST REQUIRED
- [ ] T050 [US1] Verify frontend-backend communication (create/list a task via UI) - MANUAL TEST REQUIRED

**Checkpoint**: Application fully deployed and functional in Minikube

---

## Phase 6: User Story 4 - Scale Application Replicas (Priority: P3)

**Goal**: Demonstrate horizontal scaling by modifying replica counts

**Independent Test**: After scaling, `kubectl get pods -l app=todo-frontend` should show 3 pods in Running status

### Implementation for User Story 4

- [x] T051 [US4] Scale frontend to 3 replicas (run `helm upgrade todo-frontend helm/frontend --set replicaCount=3`)
- [x] T052 [US4] Verify 3 frontend pods are running (run `kubectl get pods -l app=todo-frontend`)
- [x] T053 [US4] Scale backend to 2 replicas (run `helm upgrade todo-backend helm/backend --set replicaCount=2`)
- [x] T054 [US4] Verify 2 backend pods are running (run `kubectl get pods -l app=todo-backend`)
- [ ] T055 [US4] Verify application still works after scaling (access frontend, create task) - MANUAL TEST REQUIRED

**Checkpoint**: Scaling demonstrated successfully

---

## Phase 7: User Story 5 - AI-Assisted Infrastructure Generation (Priority: P2)

**Goal**: Document that all infrastructure artifacts were generated using AI tools

**Independent Test**: Review artifact generation logs/prompts showing AI tool usage

### Documentation for User Story 5

- [x] T056 [US5] Document AI commands used for Dockerfile generation in specs/002-local-k8s-deploy/ai-generation-log.md
- [x] T057 [US5] Document AI commands used for Helm chart generation in specs/002-local-k8s-deploy/ai-generation-log.md
- [x] T058 [US5] Document AI commands used for deployment operations in specs/002-local-k8s-deploy/ai-generation-log.md

**Checkpoint**: AI-assisted workflow fully documented

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and cleanup

- [x] T059 Verify all success criteria from spec.md are met
- [ ] T060 Run quickstart.md validation (fresh deployment test) - MANUAL TEST REQUIRED
- [x] T061 [P] Update README with Kubernetes deployment instructions
- [ ] T062 Clean up any test resources (optional: `helm uninstall`, `minikube stop`) - OPTIONAL

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup)
    │
    ▼
Phase 2 (Foundational - Next.js config)
    │
    ▼
Phase 3 (US2 - Container Images)
    │
    ▼
Phase 4 (US3 - Helm Charts)
    │
    ▼
Phase 5 (US1 - Deployment)  ◄── MVP Checkpoint
    │
    ▼
Phase 6 (US4 - Scaling)
    │
    ▼
Phase 7 (US5 - Documentation)
    │
    ▼
Phase 8 (Polish)
```

### User Story Dependencies

- **User Story 2 (Container Images)**: Depends on Phase 2 (Next.js config) - BLOCKS US1, US3
- **User Story 3 (Helm Charts)**: Depends on US2 (images must exist for deployment) - BLOCKS US1
- **User Story 1 (Deployment)**: Depends on US2 (images) and US3 (charts) - CORE DELIVERABLE
- **User Story 4 (Scaling)**: Depends on US1 (must be deployed first)
- **User Story 5 (AI Documentation)**: Can be done in parallel with implementation, finalize after

### Parallel Opportunities

Within Phase 3 (US2 - Container Images):
- T010 and T011 (generate Dockerfiles) can run in parallel
- T014 and T015 (test containers) can run in parallel

Within Phase 4 (US3 - Helm Charts):
- T019-T032 (all chart generation tasks) can run in parallel
- T033-T036 (validation) must wait for generation

Within Phase 5 (US1 - Deployment):
- Must be sequential: backend deploy → verify → frontend deploy → verify

---

## Parallel Example: Helm Chart Generation

```bash
# Launch all chart metadata tasks together:
Task: "Generate frontend Helm Chart.yaml in helm/frontend/Chart.yaml"
Task: "Generate backend Helm Chart.yaml in helm/backend/Chart.yaml"
Task: "Generate frontend values.yaml in helm/frontend/values.yaml"
Task: "Generate backend values.yaml in helm/backend/values.yaml"

# Launch all template generation together:
Task: "Generate frontend deployment.yaml in helm/frontend/templates/deployment.yaml"
Task: "Generate backend deployment.yaml in helm/backend/templates/deployment.yaml"
Task: "Generate frontend service.yaml in helm/frontend/templates/service.yaml"
Task: "Generate backend service.yaml in helm/backend/templates/service.yaml"
```

---

## Implementation Strategy

### MVP First (User Story 1 Completion)

1. Complete Phase 1: Setup (verify tools, start Minikube)
2. Complete Phase 2: Foundational (update next.config.ts)
3. Complete Phase 3: User Story 2 (build container images)
4. Complete Phase 4: User Story 3 (create Helm charts)
5. Complete Phase 5: User Story 1 (deploy to Minikube)
6. **STOP and VALIDATE**: Both pods running, frontend accessible, backend responding

### Incremental Delivery

1. Setup + Foundational → Environment ready
2. Add US2 (Container Images) → Images built and loadable
3. Add US3 (Helm Charts) → Charts validated
4. Add US1 (Deployment) → **MVP COMPLETE** - App running in Minikube
5. Add US4 (Scaling) → Scaling demonstrated
6. Add US5 (Documentation) → AI workflow documented

---

## Task Summary

| Phase | User Story | Task Count | Parallel Tasks |
|-------|------------|------------|----------------|
| 1 | Setup | 8 | 0 |
| 2 | Foundational | 1 | 0 |
| 3 | US2 - Container Images | 9 | 4 |
| 4 | US3 - Helm Charts | 18 | 14 |
| 5 | US1 - Deployment | 14 | 0 |
| 6 | US4 - Scaling | 5 | 0 |
| 7 | US5 - Documentation | 3 | 0 |
| 8 | Polish | 4 | 1 |
| **Total** | | **62** | **19** |

---

## Notes

- All tasks marked [P] can run in parallel within their phase
- [Story] label maps task to specific user story for traceability
- Commit after each phase or logical group
- Stop at MVP (Phase 5) to validate core functionality before extras
- FR-009 and FR-010 require AI generation - document all prompts used
