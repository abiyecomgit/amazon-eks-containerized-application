# Build, Scale & Monitor a Containerized Application on Amazon EKS

## Project Overview

This project demonstrates how to build, deploy, expose, autoscale, load test, and monitor a containerized application using Amazon EKS and Kubernetes.

The application was containerized with Docker, deployed to Amazon EKS using Helm, exposed through an AWS Load Balancer, automatically scaled using the Kubernetes Horizontal Pod Autoscaler (HPA), and monitored using Amazon CloudWatch Container Insights.

A Break-It Test was also performed to compare application behavior with and without autoscaling.

---

## Architecture

```text
User
 |
 v
AWS Load Balancer
 |
 v
Kubernetes Service
 |
 v
Kubernetes Deployment
 |
 v
Application Pods
 |
 v
Docker Container / Flask App :5000
```

### Autoscaling

```text
Application CPU
 |
 v
Metrics Server
 |
 v
Horizontal Pod Autoscaler
 |
 v
Deployment
 |
 v
1 - 6 Application Pods
```

### Monitoring

```text
Amazon EKS
 |
 v
CloudWatch Observability Add-on
 |
 +--> CloudWatch Agent
 +--> Fluent Bit
 +--> Node Exporter
 +--> kube-state-metrics
 |
 v
CloudWatch Container Insights
```

---

## Technologies Used

- AWS
- Amazon EKS
- Kubernetes
- Docker
- Docker Hub
- Helm
- Horizontal Pod Autoscaler (HPA)
- Kubernetes Metrics Server
- Amazon CloudWatch
- CloudWatch Container Insights
- AWS Load Balancer
- AWS CLI
- eksctl
- Python
- Flask

---

## Project Structure

```text
eks-project-rebuild/
|
├── app/
│   ├── Dockerfile
│   ├── app.py
│   └── requirements.txt
|
├── eks-project/
│   ├── Chart.yaml
│   ├── values.yaml
│   ├── cloudwatch-pod-identity-trust.json
│   └── templates/
│       ├── deployment.yaml
│       ├── service.yaml
│       ├── hpa.yaml
│       ├── serviceaccount.yaml
│       └── ...
|
├── docs/
│   └── EKS-Project-Documentation.pdf
|
├── .gitignore
└── README.md
```

---

## EKS Cluster Configuration

- Cluster: `enterprise-cluster`
- AWS Region: `us-west-2`
- Managed Node Group: `standard-workers`
- Instance Type: `t3.medium`
- Desired Nodes: `3`
- Minimum Nodes: `3`
- Maximum Nodes: `6`

---

## Docker Image

The Flask application was containerized using Docker.

Because the development machine uses Apple Silicon while the EKS worker nodes use AMD64, the image was built for the `linux/amd64` platform.

```bash
docker build --platform linux/amd64 \
  -t iyeredock3132/eks-app:2.0 .
```

The image was pushed to Docker Hub:

```bash
docker push iyeredock3132/eks-app:2.0
```

---

## EKS Cluster Creation

The EKS cluster was created using `eksctl`:

```bash
eksctl create cluster \
  --name enterprise-cluster \
  --region us-west-2 \
  --nodegroup-name standard-workers \
  --node-type t3.medium \
  --nodes 3 \
  --nodes-min 3 \
  --nodes-max 6 \
  --managed
```

Connect `kubectl`:

```bash
aws eks --region us-west-2 \
  update-kubeconfig \
  --name enterprise-cluster
```

Verify:

```bash
kubectl get nodes
```

---

## Helm Deployment

The application is managed using the `eks-project` Helm chart.

Important resource settings:

```yaml
resources:
  requests:
    cpu: 50m
    memory: 64Mi
  limits:
    cpu: 500m
    memory: 512Mi
```

The Kubernetes Service uses:

```yaml
service:
  type: LoadBalancer
  port: 80
```

Deploy or update the application:

```bash
helm upgrade --install eks-project ./eks-project
```

---

## Horizontal Pod Autoscaler

HPA was configured with:

```yaml
autoscaling:
  enabled: true
  minReplicas: 1
  maxReplicas: 6
  targetCPUUtilizationPercentage: 70
```

Verify:

```bash
kubectl get hpa
```

The HPA automatically adjusts application replicas based on CPU utilization.

---

## HPA Load Test

Traffic was generated against the Kubernetes Service using BusyBox.

During increased traffic, CPU utilization increased and HPA automatically scaled the application from:

```text
1 Pod --> 6 Pods
```

After the load was removed and CPU utilization dropped, Kubernetes eventually scaled the application back down:

```text
6 Pods --> 1 Pod
```

This demonstrated both HPA scale-up and scale-down behavior.

---

## Break-It Test

HPA was temporarily disabled to observe the application's behavior without automatic scaling.

Three load-generator Pods were used to increase traffic.

The application remained at:

```text
1 Application Pod
```

Application CPU was observed as high as:

```text
392m
```

against its configured:

```text
500m CPU limit
```

Because HPA was disabled, Kubernetes did not create additional application Pods.

---

## HTTP Performance Test

Ten external requests were sent through the AWS Load Balancer while the application was under load.

Results:

- HTTP success: `10/10 HTTP 200`
- Application remained available
- Response-time spikes were observed
- Approximately `1.04 seconds`
- Maximum observed approximately `1.22 seconds`

This demonstrated that the application remained available but experienced variable response times while a single Pod handled increased workload.

---

## CloudWatch Monitoring

Amazon CloudWatch Observability was configured for the EKS cluster.

Monitoring components included:

- CloudWatch Agent
- Fluent Bit
- Node Exporter
- kube-state-metrics
- CloudWatch Observability Controller
- CloudWatch Cluster Scraper

CloudWatch Container Insights was used to monitor:

- CPU utilization
- Memory utilization
- Pod health
- Node health
- Kubernetes workloads
- Logs
- Cluster performance

Verify:

```bash
kubectl get pods -n amazon-cloudwatch
```

---

## Test Summary

| Test | Result |
|---|---|
| Docker application | Passed |
| EKS deployment | Passed |
| Helm deployment | Passed |
| LoadBalancer access | Passed |
| Metrics collection | Passed |
| HPA scale-up | 1 → 6 Pods |
| HPA scale-down | 6 → 1 Pod |
| Break-It Test | Passed |
| Peak observed CPU without HPA | 392m / 500m |
| HTTP requests | 10/10 HTTP 200 |
| Maximum observed response time | ~1.22 seconds |
| CloudWatch monitoring | Operational |

---

## What I Learned

This project helped demonstrate how Docker, Kubernetes, Amazon EKS, Helm, HPA, AWS Load Balancing, and CloudWatch work together.

The HPA test demonstrated how Kubernetes can automatically increase application capacity when demand increases and reduce capacity when demand decreases.

The Break-It Test demonstrated why autoscaling is important. Without HPA, increased traffic placed additional CPU pressure on a single application Pod and resulted in variable response times.

CloudWatch Container Insights provided visibility into the health and performance of the cluster, nodes, Pods, and workloads.

---

## Full Project Documentation

Detailed step-by-step project documentation is available here:

`docs/EKS-Project-Documentation.pdf`

---

## Author

**Abraham Iyere**

DevOps / Cloud Engineering Project
