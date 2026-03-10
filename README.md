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


kubectl logs
kubectl describe
kubectl exec

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

# Week 3 – Networking + Ingress + TLS

# Week 4 – CI/CD Pipeline

# Week 5 – Helm & Structured Deployments

# Week 6 – Monitoring & Observability
