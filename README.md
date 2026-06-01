# Terraform-Based Cloud Resource Provisioning & Python MLOps Monitoring Stub

## Overview

This project demonstrates two core DevOps/MLOps capabilities:

1. **Terraform Infrastructure as Code (IaC)** for provisioning a basic AWS cloud resource.
2. **Python-based MLOps Monitoring Stub** for monitoring model endpoint latency and detecting feature drift.

The project is intended as a simple reference implementation showcasing Infrastructure as Code, cloud storage best practices, and foundational MLOps monitoring concepts.

---

## Components

### 1. Terraform Configuration

The Terraform code provisions an Amazon S3 bucket for storing machine learning model artifacts with:

* Bucket Versioning
* Server-Side Encryption (AES256)
* Public Access Blocking
* Lifecycle Management
* Automated archival of older model versions to Glacier Instant Retrieval

### 2. Python MLOps Monitoring Stub

The monitoring script simulates a deployed ML model endpoint and performs:

* Endpoint latency monitoring
* P95 latency calculation
* Feature drift detection using Population Stability Index (PSI)
* Alert generation for SLA breaches and drift conditions
* Structured logging for integration with monitoring platforms

---

## Project Structure

```text
.
├── main.tf
├── model_monitor.py
└── README.md
```

---

## Terraform Features

### Amazon S3 Model Artifact Storage

* Secure artifact storage
* Version history preservation
* Cost optimization through lifecycle policies

### Lifecycle Policy

| Condition                      | Action                            |
| ------------------------------ | --------------------------------- |
| Non-current version > 60 days  | Move to Glacier Instant Retrieval |
| Non-current version > 730 days | Delete                            |

---

## Python Monitoring Features

### Latency Monitoring

Monitors endpoint response times and raises alerts when the P95 latency exceeds the configured SLA.

```python
LATENCY_SLA_MS = 300
```

### Feature Drift Detection

Uses Population Stability Index (PSI) to compare baseline and current prediction distributions.

```python
DRIFT_PSI_THRESHOLD = 0.2
```

### Alert Generation

Example:

```json
{
  "alert_type": "DRIFT",
  "severity": "WARNING",
  "message": "Feature confidence PSI exceeded threshold"
}
```

---

## Usage

### Deploy Infrastructure

```bash
terraform init
terraform plan
terraform apply
```

### Run Monitoring Stub

```bash
python model_monitor.py
```

---

## Sample Workflow

```text
Terraform
    │
    ▼
Provision S3 Bucket
    │
    ▼
Store Model Artifacts
    │
    ▼
Deploy Model Endpoint
    │
    ▼
Run model_monitor.py
    │
    ├── Monitor Latency
    ├── Detect Drift
    └── Generate Alerts
```

---

## Technologies Used

* Terraform
* AWS S3
* Python
* Infrastructure as Code (IaC)
* MLOps Monitoring
* Population Stability Index (PSI)

---

## Future Enhancements

* CloudWatch Integration
* Slack/PagerDuty Notifications
* Prometheus Metrics
* Grafana Dashboards
* AWS KMS Encryption
* MLflow Integration

---

## License

MIT License
