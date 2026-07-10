# Architecture Design Documentation

This document explains the technical choices, design patterns, and system components of the AI Platform Infrastructure Automation Framework.

---

## 1. Architectural Principles

The architecture follows modern MLOps and Cloud Native Infrastructure principles:
* **Infrastructure as Code (IaC)**: The system configuration is fully declarative and managed by Ansible.
* **Separation of Concerns**: Compute (FastAPI app, MLflow engine) is separated from storage (PostgreSQL metadata database, MinIO object storage).
* **Decoupled Monitoring**: Grafana and Prometheus run in an independent namespace (`monitoring`), tracking metrics from the cluster daemon without intervening in platform execution.
* **Local Developer Simplicity**: Uses a local image loader workflow (`docker save` + `k3s ctr import`) to load built images into Kubernetes without requiring a public/private registry.

---

## 2. Component Design Choices

### Container & Orchestration Layer: Docker, Containerd, and K3s
* **Docker CE**: Installed on the underlying Linux nodes as the development container engine, allowing operators to run standard docker commands.
* **K3s (Lightweight Kubernetes)**: Chosen over Kubeadm. It installs as a single binary, is fully CNCF certified, and has a smaller resource footprint (ideal for dev/stage VMs or small bare-metal clusters), while supporting standard Helm charts and local storage out of the box.
* **Disable Traefik**: K3s defaults to Traefik. We disable Traefik in our Ansible configuration (`--disable=traefik`) to deploy NGINX Ingress Controller, which is the enterprise standard for enterprise ingress pathing, annotations, and integrations.

### Storage & MLOps Platform Layer
* **PostgreSQL (Metadata DB)**: Configured as a Deployment with local persistent volume storage. It acts as the backend store for MLflow, tracking experiment IDs, run IDs, metrics, tags, parameters, and system users.
* **MinIO (Object Storage)**: Replaces cloud-specific storage (AWS S3, GCP GCS) for local or on-prem environments. Exposes standard, S3-compatible APIs for model storage.
* **MLflow Tracking Server**: Connected directly to the PostgreSQL instance via SQLAlchemy URL and the MinIO bucket via S3 API, creating a robust, unified experiment catalog.

### Monitoring & Observability Layer
* **Prometheus community charts**: Deployed via Helm to collect host OS resource consumption metrics (via Node Exporter), cluster daemon stats, and pod execution statistics (via Kube State Metrics).
* **Grafana dashboard provisioning**: Configured to watch for dashboard configurations using a sidecar auto-discovery container. This prevents storing credentials in dashboards and automatically loads the Node Exporter and Pod metrics layout files.

---

## 3. Security Design & Hardening

* **Ansible Vault**: All sensitive database passwords, dashboard logins, and access keys are stored in `group_vars/vault.yml`, which can be safely encrypted and committed to Git.
* **Least Privilege Access**: Dedicated system user `deploy` created with selective SSH key authentication and passwordless sudo configurations restricted to system binaries.
* **UFW Firewall Rules**: Restricts incoming traffic, allowing ports only for SSH, HTTP/HTTPS web endpoints, Kubernetes API traffic, Kubelet control, and inter-node vxlan flannel operations.
* **Kernel Level Hardening**: Configures sysctl flags to prevent IP spoofing, drop source-routed packets, configure SYN cookie flood defenses, and expand maximum file descriptor boundaries.
