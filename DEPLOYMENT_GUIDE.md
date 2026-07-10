# Deployment Guide & Operations Manual

This guide describes how to run the AI Platform Infrastructure Automation Framework to set up the environments.

---

## 1. Prerequisites

### Control Node (Your Operator Machine)
* Ansible >= 2.12 installed.
* Python 3 with `pip` installed.
* SSH keys generated and distributed to the target hosts.
* **Kubernetes collections** installed on the control node:
  ```bash
  ansible-galaxy collection install kubernetes.core
  ```

### Target Nodes (Servers to configure)
* Ubuntu 20.04 or 22.04 LTS installed.
* SSH service running and accessible.
* Direct internet access (to download Docker packages, Helm charts, and images).

---

## 2. Configuration & Environments

### Step 1: Update Inventories
Update the hosts configuration files under `inventories/` to map to your target node IPs:
* **Dev environment**: [inventories/dev/hosts.ini](file:///d:/ansible-ai-platform-automation/inventories/dev/hosts.ini)
* **Stage environment**: [inventories/stage/hosts.ini](file:///d:/ansible-ai-platform-automation/inventories/stage/hosts.ini)
* **Prod environment**: [inventories/prod/hosts.ini](file:///d:/ansible-ai-platform-automation/inventories/prod/hosts.ini)

### Step 2: Configure Vault
Encrypt your sensitive credentials using Ansible Vault before pushing to repository control:
```bash
ansible-vault encrypt group_vars/vault.yml
```
You will be prompted to enter a vault password. To run the playbook with the encrypted vault, add the `--ask-vault-pass` flag.

---

## 3. Launching Deployment

### One-Command Full Deployment
To deploy the entire stack (common system, docker, kubernetes cluster, mlflow components, monitoring stack, and FastAPI app) run:
```bash
ansible-playbook -i inventories/dev/hosts.ini playbooks/site.yml --ask-vault-pass
```

### Selective Component Deployment (Using Tags / Playbooks)
You can choose to deploy only specific layers by executing their respective playbooks:

1. **System & Docker Layer**:
   ```bash
   ansible-playbook -i inventories/dev/hosts.ini playbooks/docker.yml
   ```
2. **Kubernetes Clustering**:
   ```bash
   ansible-playbook -i inventories/dev/hosts.ini playbooks/kubernetes.yml
   ```
3. **MLOps Platform Services (Postgres, MinIO, MLflow)**:
   ```bash
   ansible-playbook -i inventories/dev/hosts.ini playbooks/mlflow.yml --ask-vault-pass
   ```
4. **Monitoring Stack (Prometheus & Grafana)**:
   ```bash
   ansible-playbook -i inventories/dev/hosts.ini playbooks/monitoring.yml --ask-vault-pass
   ```
5. **AI Serving App**:
   ```bash
   ansible-playbook -i inventories/dev/hosts.ini playbooks/ai-app.yml
   ```

---

## 4. Verification & Testing

### Step 1: Mapping Local Hosts
The ingress controller listens on standard HTTP port 80. To access the dashboard domains, append the following mappings to `/etc/hosts` (Linux/macOS) or `C:\Windows\System32\drivers\etc\hosts` (Windows), replacing `MASTER_IP` with your master node's IP:
```text
MASTER_IP   mlflow.local
MASTER_IP   minio.local
MASTER_IP   grafana.local
MASTER_IP   ai-app.local
```

### Step 2: Validate HTTP Endpoints
Once mapped, run these validations:

* **FastAPI Model `/predict` Check**:
  ```bash
  curl http://ai-app.local/predict
  ```
  Expected Output:
  ```json
  {
    "prediction": "AI Platform Engineer",
    "served_by": "fastapi-ai-app-7bf485d4dc-abc12",
    "timestamp": 1694382942.312
  }
  ```

* **MLflow Tracking Server Check**:
  Open `http://mlflow.local` in your browser to verify the MLflow Tracking dashboard.

* **MinIO Console Check**:
  Open `http://minio.local` in your browser. Log in using the credentials in `group_vars/vault.yml` (`minioadmin` by default) to inspect the `mlflow` bucket.

* **Grafana Dashboards Check**:
  Open `http://grafana.local` in your browser. Log in using user `admin` and password from `vault.yml`. Go to Dashboards to view the Node Host Metrics and Kubernetes metrics dashboards.

---

## 5. Troubleshooting & Diagnostic Commands

* **List active pods and status**:
  ```bash
  kubectl get pods -A
  ```
* **Fetch logs for the AI Model serving app**:
  ```bash
  kubectl logs -n mlops deployment/fastapi-ai-app
  ```
* **Verify K3s nodes configuration**:
  ```bash
  kubectl get nodes -o wide
  ```
