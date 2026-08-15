# Local Private Docker Registry Blueprint for vSphere/ESXi

This document provides a step-by-step strategy to deploy and configure a secure, local, private Docker registry hosted directly on the ESXi/vSphere environment.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        vSphere Cluster                          │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐    ┌─────────────────┐                    │
│  │   ESXi Host 1   │    │   ESXi Host 2   │   ...              │
│  │  ┌───────────┐  │    │  ┌───────────┐  │                    │
│  │  │  Registry │  │    │  │  K8s Node │  │                    │
│  │  │   VM/Appliance  │    │  │  (Worker) │  │                    │
│  │  └───────────┘  │    │  └───────────┘  │                    │
│  └─────────────────┘    └─────────────────┘                    │
│         │                       │                               │
│         └───────────────────────┼─────────────────────────────┘ │
│                                 ▼                               │
│                    ┌─────────────────────────┐                 │
│                    │   Shared Datastore      │                 │
│                    │   (VMFS/NFS/vSAN)       │                 │
│                    │   Registry Storage      │                 │
│                    └─────────────────────────┘                 │
└─────────────────────────────────────────────────────────────────┘
```

## Option 1: Harbor Registry (Recommended for Production)

Harbor is an enterprise-grade registry with built-in security, replication, and management UI.

### Prerequisites

- ESXi 7.0+ or vCenter 7.0+
- Shared datastore with minimum 100GB free space
- Static IP address for registry VM
- DNS entry: `registry.local` → registry IP
- TLS certificates (self-signed or CA-signed)

### Deployment Steps

#### 1. Prepare the Registry VM

```bash
# Create a VM for Harbor (4 vCPU, 8GB RAM, 50GB disk + 200GB data disk)
# Ubuntu 22.04 LTS recommended
```

#### 2. Install Docker and Docker Compose

```bash
# On the registry VM
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
newgrp docker

# Install docker-compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### 3. Generate TLS Certificates

```bash
# Create certificate directory
mkdir -p /opt/harbor/certs

# Generate self-signed certificate (replace with CA-signed for production)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /opt/harbor/certs/registry.local.key \
  -out /opt/harbor/certs/registry.local.crt \
  -subj "/CN=registry.local/O=Incident Response/OU=Security" \
  -addext "subjectAltName=DNS:registry.local,IP:<REGISTRY_IP>"

# Set permissions
chmod 600 /opt/harbor/certs/registry.local.key
chmod 644 /opt/harbor/certs/registry.local.crt
```

#### 4. Download and Configure Harbor

```bash
# Download Harbor offline installer
wget https://github.com/goharbor/harbor/releases/download/v2.10.0/harbor-offline-installer-v2.10.0.tgz
tar xzf harbor-offline-installer-v2.10.0.tgz
cd harbor

# Copy certificate
cp /opt/harbor/certs/registry.local.crt ./common/config/nginx/cert/
cp /opt/harbor/certs/registry.local.key ./common/config/nginx/cert/

# Configure harbor.yml
cat > harbor.yml <<EOF
hostname: registry.local
http:
  port: 80
https:
  port: 443
  certificate: /common/config/nginx/cert/registry.local.crt
  private_key: /common/config/nginx/cert/registry.local.key

harbor_admin_password: "ChangeMeSecurePassword123!"
database:
  password: "ChangeMeDBPassword123!"
  max_idle_conns: 50
  max_open_conns: 100

data_volume: /data/harbor
trivy:
  ignore_unfixed: false
  skip_update: false
  offline_scan: false

jobservice:
  max_job_workers: 10
  log_level: info

notification:
  webhook_job_max_retry: 3

chart:
  absolute_url: disabled

log:
  level: info
  local:
    rotate_count: 50
    rotate_size: 200M
    location: /var/log/harbor

proxy:
  http_proxy:
  https_proxy:
  no_proxy: "127.0.0.1,localhost,.local,.internal"
EOF
```

#### 5. Install Harbor

```bash
sudo ./install.sh --with-trivy --with-chartmuseum
```

#### 6. Verify Installation

```bash
# Check services
docker-compose -f /opt/harbor/docker-compose.yml ps

# Test registry access
curl -k https://registry.local/v2/_catalog
```

---

## Option 2: Basic Docker Registry (Lightweight)

For simpler deployments without Harbor's overhead.

### Deployment Steps

#### 1. Create Registry VM

```bash
# Minimal VM: 2 vCPU, 4GB RAM, 20GB OS disk + 100GB data disk
# Ubuntu 22.04 LTS
```

#### 2. Install Docker

```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
```

#### 3. Generate Certificates

```bash
mkdir -p /opt/registry/certs
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /opt/registry/certs/registry.local.key \
  -out /opt/registry/certs/registry.local.crt \
  -subj "/CN=registry.local" \
  -addext "subjectAltName=DNS:registry.local,IP:<REGISTRY_IP>"
```

#### 3. Create Registry Configuration

```bash
mkdir -p /opt/registry/config /opt/registry/data

cat > /opt/registry/config/config.yml <<EOF
version: 0.1
log:
  level: info
  fields:
    service: registry
storage:
  filesystem:
    rootdirectory: /var/lib/registry
  delete:
    enabled: true
  maintenance:
    uploadpurging:
      enabled: true
      age: 168h
      interval: 24h
      dryrun: false
auth:
  htpasswd:
    realm: basic-realm
    path: /auth/htpasswd
http:
  addr: :443
  headers:
    X-Content-Type-Options: [nosniff]
  tls:
    certificate: /certs/registry.local.crt
    key: /certs/registry.local.key
health:
  storagedriver:
    enabled: true
    interval: 10s
    threshold: 3
compatibility:
  schema1:
    enabled: true
EOF
```

#### 4. Create Authentication

```bash
# Install apache2-utils for htpasswd
sudo apt-get update && sudo apt-get install -y apache2-utils

# Create password file
mkdir -p /opt/registry/auth
htpasswd -Bbn admin "SecurePassword123!" > /opt/registry/auth/htpasswd
```

#### 5. Run Registry Container

```bash
docker run -d \
  --name registry \
  --restart=always \
  -p 443:443 \
  -v /opt/registry/data:/var/lib/registry \
  -v /opt/registry/config:/etc/docker/registry \
  -v /opt/registry/certs:/certs \
  -v /opt/registry/auth:/auth \
  registry:2.8
```

#### 6. Verify

```bash
curl -u admin:SecurePassword123! -k https://registry.local/v2/_catalog
```

---

## Configuring Kubernetes Nodes to Trust the Registry

### For containerd (Standard in Kubernetes 1.24+)

#### 1. Copy CA Certificate to All Nodes

```bash
# On each Kubernetes node (or via DaemonSet)
sudo mkdir -p /etc/containerd/certs.d/registry.local
sudo cp registry.local.crt /etc/containerd/certs.d/registry.local/ca.crt
```

#### 2. Configure containerd

```bash
# Edit /etc/containerd/config.toml
sudo tee /etc/containerd/config.toml > /dev/null <<EOF
version = 2
[plugins."io.containerd.grpc.v1.cri".registry]
  [plugins."io.containerd.grpc.v1.cri".registry.mirrors]
    [plugins."io.containerd.grpc.v1.cri".registry.mirrors."registry.local"]
      endpoint = ["https://registry.local"]
  [plugins."io.containerd.grpc.v1.cri".registry.configs]
    [plugins."io.containerd.grpc.v1.cri".registry.configs."registry.local".tls]
      ca_file = "/etc/containerd/certs.d/registry.local/ca.crt"
      insecure_skip_verify = false
EOF
```

#### 3. Restart containerd

```bash
sudo systemctl restart containerd
```

### For Docker Engine (Legacy)

```bash
# On each node
sudo mkdir -p /etc/docker/certs.d/registry.local
sudo cp registry.local.crt /etc/docker/certs.d/registry.local/ca.crt

# Configure daemon.json
sudo tee /etc/docker/daemon.json > /dev/null <<EOF
{
  "insecure-registries": [],
  "registry-mirrors": [],
  "exec-opts": ["native.cgroupdriver=systemd"]
}
EOF

sudo systemctl restart docker
```

---

## Configuring Kubernetes to Pull from Private Registry

### 1. Create Image Pull Secret

```bash
# Create namespace if not exists
kubectl create namespace incident-response

# Create docker-registry secret
kubectl create secret docker-registry registry-credentials \
  --docker-server=registry.local \
  --docker-username=admin \
  --docker-password="SecurePassword123!" \
  --docker-email=admin@local \
  -n incident-response
```

### 2. Patch ServiceAccounts to Use Secret

```bash
# Patch default SA in incident-response namespace
kubectl patch serviceaccount default \
  -n incident-response \
  -p '{"imagePullSecrets": [{"name": "registry-credentials"}]}'

# Patch component-specific SAs
kubectl patch serviceaccount telemetry-sensor \
  -n incident-response \
  -p '{"imagePullSecrets": [{"name": "registry-credentials"}]}'

kubectl patch serviceaccount threat-contextualizer \
  -n incident-response \
  -p '{"imagePullSecrets": [{"name": "registry-credentials"}]}'

kubectl patch serviceaccount reconciler-engine \
  -n incident-response \
  -p '{"imagePullSecrets": [{"name": "registry-credentials"}]}'
```

### 3. Update Deployment Image References

```yaml
# In kustomization.yaml or deployment manifests
images:
- name: registry.local/incident-response/telemetry-sensor
  newTag: "1.0.0"
- name: registry.local/incident-response/threat-contextualizer
  newTag: "1.0.0"
- name: registry.local/incident-response/reconciler-engine
  newTag: "1.0.0"
```

---

## Building and Pushing Images to Local Registry

### 1. Build All Images

```bash
# From project root
docker build -t registry.local/incident-response/telemetry-sensor:1.0.0 ./cmd/telemetry-sensor
docker build -t registry.local/incident-response/threat-contextualizer:1.0.0 ./cmd/threat-contextualizer
docker build -t registry.local/incident-response/reconciler-engine:1.0.0 ./cmd/reconciler-engine
```

### 2. Login and Push

```bash
# Login to registry
docker login registry.local -u admin -p "SecurePassword123!"

# Push images
docker push registry.local/incident-response/telemetry-sensor:1.0.0
docker push registry.local/incident-response/threat-contextualizer:1.0.0
docker push registry.local/incident-response/reconciler-engine:1.0.0
```

### 3. Verify in Registry

```bash
curl -u admin:SecurePassword123! -k https://registry.local/v2/_catalog
# Should show: incident-response/telemetry-sensor, incident-response/threat-contextualizer, incident-response/reconciler-engine
```

---

## Automated Image Build Pipeline (Optional)

### Using GitLab CI / GitHub Actions / Jenkins

```yaml
# .gitlab-ci.yml example
stages:
  - build
  - test
  - push

variables:
  REGISTRY: registry.local
  IMAGE_PREFIX: incident-response

build:telemetry-sensor:
  stage: build
  image: docker:24
  services:
    - docker:24-dind
  script:
    - docker build -t $REGISTRY/$IMAGE_PREFIX/telemetry-sensor:$CI_COMMIT_SHA ./cmd/telemetry-sensor
    - docker push $REGISTRY/$IMAGE_PREFIX/telemetry-sensor:$CI_COMMIT_SHA
  only:
    - main
    - tags

build:threat-contextualizer:
  stage: build
  image: docker:24
  services:
    - docker:24-dind
  script:
    - docker build -t $REGISTRY/$IMAGE_PREFIX/threat-contextualizer:$CI_COMMIT_SHA ./cmd/threat-contextualizer
    - docker push $REGISTRY/$IMAGE_PREFIX/threat-contextualizer:$CI_COMMIT_SHA
  only:
    - main
    - tags

build:reconciler-engine:
  stage: build
  image: docker:24
  services:
    - docker:24-dind
  script:
    - docker build -t $REGISTRY/$IMAGE_PREFIX/reconciler-engine:$CI_COMMIT_SHA ./cmd/reconciler-engine
    - docker push $REGISTRY/$IMAGE_PREFIX/reconciler-engine:$CI_COMMIT_SHA
  only:
    - main
    - tags
```

---

## Security Hardening Checklist

- [ ] Use CA-signed certificates (not self-signed) for production
- [ ] Enable authentication (htpasswd or OIDC/LDAP)
- [ ] Configure vulnerability scanning (Trivy/Clair)
- [ ] Enable image signing (Notary/Cosign)
- [ ] Set up replication for HA (multi-site)
- [ ] Configure retention policies
- [ ] Enable audit logging
- [ ] Restrict network access (firewall/NSG)
- [ ] Regular backup of registry data
- [ ] Monitor disk space and health
- [ ] Rotate certificates before expiry
- [ ] Use strong passwords/password policies
- [ ] Enable 2FA for Harbor UI access

---

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| `x509: certificate signed by unknown authority` | Copy CA cert to `/etc/containerd/certs.d/registry.local/ca.crt` and restart containerd |
| `no basic auth credentials` | Create docker-registry secret and patch ServiceAccounts |
| `connection refused` | Check firewall, registry container status, and port 443 |
| `manifest unknown` | Image not pushed; verify `docker push` succeeded |
| `disk full` | Configure retention policies, run garbage collection |

### Garbage Collection

```bash
# Harbor: via UI or API
# Basic registry:
docker exec registry bin/registry garbage-collect /etc/docker/registry/config.yml --dry-run
docker exec registry bin/registry garbage-collect /etc/docker/registry/config.yml
```

---

## Network Policies for Registry Access

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-registry-egress
  namespace: incident-response
spec:
  podSelector:
    matchLabels:
      app.kubernetes.io/part-of: incident-response-loop
  policyTypes:
  - Egress
  egress:
  - to:
    - ipBlock:
        cidr: <REGISTRY_IP>/32
    ports:
    - protocol: TCP
      port: 443
  - to:
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: kube-system
    ports:
    - protocol: UDP
      port: 53
    - protocol: TCP
      port: 53
```

---

## Summary

This blueprint provides a complete strategy for deploying a secure local Docker registry on vSphere/ESXi:

1. **Harbor** for production (UI, RBAC, scanning, replication)
2. **Basic Registry** for lightweight needs
3. **TLS everywhere** with proper certificate distribution
4. **Containerd configuration** on all K8s nodes
5. **ImagePullSecrets** for Kubernetes workloads
6. **Automation** via CI/CD pipelines
7. **Security hardening** checklist

The registry at `registry.local` will serve as the trusted source for all incident-response-loop images, enabling fully offline operation.