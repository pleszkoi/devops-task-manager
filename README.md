# DevOps Task Manager – Kubernetes Homelab Project

A hands-on DevOps learning project where a simple FastAPI application is gradually evolved into a fully containerized and Kubernetes-deployed microservice.

The goal of this repository is to **learn and demonstrate practical DevOps skills** including:

- containerization
- Kubernetes deployments
- infrastructure as code
- service networking
- persistent storage
- CI/CD pipelines
- monitoring and observability

This project follows a **weekly learning roadmap**, where each week introduces new DevOps concepts and tools.

---

# Repository Structure
<pre>
devops-task-manager/
│
├── app
│   └── devops_task_manager
│       ├── api
│       │   └── routes
│       │       ├── debug.py
│       │       ├── health.py
│       │       └── tasks.py
│       ├── core
│       │   └── config.py
│       ├── main.py
│       ├── models
│       │   └── task.py
│       ├── repositories
│       │   └── task_repo_memory.py
│       └── services
│           └── task_service.py
├── Dockerfile
├── k8s
│   ├── namespace.yaml
│   ├── task-manager-deployment.yaml
│   └── task-manager-service.yaml
├── README.md
├── requirements.txt
└── tests
    └── test_health.py
</pre>

---

# Week 1 – Kubernetes Basics & First Deployment

## Goal

A working **k3s Kubernetes cluster** with the first deployed application.

---

## Cluster Installation

Technology used:

- k3s

Concepts learned:

- kubeconfig
- kubectl
- namespaces
- pod lifecycle

## App + Docker

Tasks:

- Create a minimal FastAPI application
- Containerize the application with Docker
- Push the Docker image to DockerHub

## Kubernetes Deployment

Create Kubernetes resources:

- Namespace
- Deployment
- ClusterIP Service

Commands learned:

- kubectl logs
- kubectl describe
- kubectl exec

---

## Current Architecture

FastAPI Application  
↓  
Docker Container  
↓  
DockerHub Registry  
↓  
Kubernetes Deployment (k3s)  
↓  
Service  
↓  
Pods managed by ReplicaSet

---

## Experiments

Document and observe:

- What happens if a pod is deleted?
- How ReplicaSets automatically recreate pods
- How Deployments manage ReplicaSets
- Rolling updates during container image upgrades

---

## Running the Application Locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
uvicorn devops_task_manager.main:app --app-dir app --host 0.0.0.0 --port 8000
```

Open Swagger UI:

```
http://localhost:8000/docs
```

Build the Docker container image:

```bash
docker build -t devops-task-manager:0.1.0 .
```

Run the container:

```bash
docker run -p 8000:8000 devops-task-manager:0.1.0
```

Apply Kubernetes manifests:

```bash
kubectl apply -f k8s/
```

Check resources:

```bash
kubectl get all -n task-manager
```

Port forward for local testing:

```bash
kubectl port-forward svc/task-manager 8080:80 -n task-manager
```

Access the application:

```
http://localhost:8080
```

---

# Week 2 – Database + Storage (Stateful Workloads)

## Goal

Run PostgreSQL inside Kubernetes with persistent storage and connect the FastAPI application to it.

---

## What I Built

- PostgreSQL deployed inside Kubernetes
- Persistent storage using PVC (via k3s local-path provisioner)
- FastAPI app connected to PostgreSQL using SQLAlchemy
- Secrets used for database credentials
- Health endpoints extended with database readiness check
- Kubernetes readiness & liveness probes configured
- PostgreSQL migrated from Deployment → StatefulSet
- Headless Service introduced for stable network identity

---

## Kubernetes Concepts Learned

### Persistent Storage

- **PersistentVolume (PV)** – actual storage resource
- **PersistentVolumeClaim (PVC)** – request for storage
- **StorageClass** – dynamic provisioning (k3s `local-path`)

Result: data persists even if pods restart

---

### Stateful vs Stateless

| Stateless (Week 1) | Stateful (Week 2) |
|------------------|------------------|
| Pods are interchangeable | Pods have identity |
| No data persistence | Persistent storage |
| Deployment | StatefulSet |

---

### PostgreSQL as Stateful Workload

- Switched from `Deployment` → `StatefulSet`
- Stable pod identity:

```bash
postgres-0
```

- Persistent data stored in PVC
- Database survives pod restarts

---

### Headless Service

Converted PostgreSQL service to:

```yaml
clusterIP: None
```

This enables:

- Direct pod DNS resolution:

```bash
postgres-0.postgres.task-manager.svc.cluster.local
```

- No load balancing (important for databases)
- Stable network identity

## Health Checks (Production Pattern)

**Liveness**

```bash
/health
```

- Checks if app is running
- Kubernetes restarts container if it fails

**Readiness**

```bash
/ready
```

- Checks DB connectivity (SELECT 1)
- Removes pod from traffic if DB is unavailable

## Configuration & Secrets

Database connection is configured via environment variables:
- DB_HOST
- DB_PORT
- DB_NAME
- DB_USER
- DB_PASSWORD

Sensitive values are stored in Kubernetes ```Secret```.

## What I Verified

- Data persists after:
  - pod restart
  - deployment rollout
- Application reconnects to database
- Readiness probe blocks traffic when DB is unavailable
- Service routing works across multiple replicas

## Architecture (Week 2)

FastAPI (stateless)  
        ↓  
Service (ClusterIP)  
        ↓  
Pods (replicas)  
        ↓  
PostgreSQL (StatefulSet)  
        ↓  
PVC → Persistent storage  

# Week 3 – Networking + Ingress + TLS

## Goal
Expose the FastAPI application outside the cluster using Ingress and secure it with HTTPS (TLS).

---

## What I Built

- Exposed the application via Kubernetes **Ingress**
- Used **Traefik (k3s default Ingress Controller)**
- Configured **host-based routing** (`api.localhost`)
- Implemented **TLS with self-signed certificate**
- Verified full request flow from browser → backend → database
- Integrated health endpoints with real traffic

---

## Service vs Ingress

| Service | Ingress |
|--------|--------|
| Internal cluster access | External HTTP/HTTPS access |
| Routes to pods | Routes to services |
| Works on TCP level | Works on HTTP/HTTPS level |

---

## Ingress

An Ingress defines how external HTTP/HTTPS traffic reaches services inside the cluster.

Example:

```text
api.localhost → task-manager Service → FastAPI pods
```

Important:

- Ingress itself is only a declarative rule
- A controller (Traefik) is required to apply it

Traefik (Ingress Controller):

- Watches Kubernetes resources (Ingress, Services, Secrets)
- Dynamically builds routing configuration
- Handles incoming HTTP/HTTPS traffic

## TLS (HTTPS)

Generated a Self-Signed Certificate for:

```text
api.localhost
```

Used to secure traffic via HTTPS.

## Kubernetes TLS Secret

Created a secret:

```text
task-manager-tls
```

Used by Ingress for TLS termination.

## TLS Termination

TLS is handled at the Ingress level (Traefik):

HTTPS request 
↓ 
Traefik (TLS termination) 
↓ 
HTTP to Service 
↓ 
FastAPI 

## Health Checks in Real Traffic

Verified endpoints through Ingress:

- /health → application alive
- /ready → database connectivity check

Example:

```bash
curl -k https://api.localhost/health
curl -k https://api.localhost/ready
```

## Architecture (Week 3)

User (Browser / Curl) 
        ↓ 
DNS (api.localhost) 
        ↓ 
Traefik (Ingress Controller) 
        ↓ 
TLS Termination 
        ↓ 
Ingress Rule (Host-based routing) 
        ↓ 
Service (ClusterIP) 
        ↓ 
FastAPI Pods 
        ↓ 
PostgreSQL (StatefulSet) 
        ↓ 
Persistent Volume 

# Week 4 – CI/CD Pipeline

# Week 5 – Helm & Structured Deployments

# Week 6 – Monitoring & Observability
