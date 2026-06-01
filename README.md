# MLOps Model Artifact Storage on AWS S3 using Terraform

## Overview

This project provisions a secure and production-ready Amazon S3 bucket for storing Machine Learning model artifacts using Terraform.

The solution follows Infrastructure as Code (IaC) principles and incorporates security, version control, encryption, and lifecycle management best practices commonly used in MLOps environments.

---

## Architecture

```text
ML Training Pipeline
        │
        ▼
  Model Artifact
 (model.pkl, .onnx)
        │
        ▼
    Amazon S3
        │
        ├── Versioning Enabled
        ├── Server-Side Encryption
        ├── Public Access Blocked
        └── Lifecycle Management
                │
                ▼
      Glacier Instant Retrieval
      (Old Model Versions)
```

---

## Features

### Secure Storage

* Amazon S3 bucket for model artifacts
* Server-side encryption enabled (AES256)
* All public access blocked

### Version Control

* S3 Versioning enabled
* Preserves historical model versions
* Supports rollback to previous model artifacts

### Cost Optimization

Lifecycle policy automatically:

* Transitions non-current model versions to Glacier Instant Retrieval after 60 days
* Deletes non-current versions after 730 days

### Infrastructure as Code

* Fully managed through Terraform
* Repeatable and version-controlled deployments
* Easy integration with CI/CD pipelines

---

## Project Structure

```text
.
├── main.tf
├── variables.tf      (optional)
├── outputs.tf        (optional)
├── terraform.tfvars  (optional)
└── README.md
```

---

## Prerequisites

Before deploying, ensure you have:

* AWS Account
* AWS CLI configured
* Terraform v1.5 or later
* IAM permissions for S3 resource creation

Verify installation:

```bash
terraform -version
aws sts get-caller-identity
```

---

## Configuration

Default values:

| Variable    | Description           | Default                    |
| ----------- | --------------------- | -------------------------- |
| aws_region  | AWS deployment region | us-east-1                  |
| bucket_name | S3 bucket name        | mlops-model-artifacts-prod |

Example customization:

```hcl
bucket_name = "my-company-ml-models"
aws_region  = "us-east-1"
```

---

## Deployment Steps

### 1. Initialize Terraform

```bash
terraform init
```

Downloads the AWS provider and initializes the working directory.

---

### 2. Validate Configuration

```bash
terraform validate
```

Checks Terraform syntax and configuration validity.

---

### 3. Review Execution Plan

```bash
terraform plan
```

Shows resources that Terraform will create.

---

### 4. Deploy Infrastructure

```bash
terraform apply
```

Type:

```text
yes
```

to confirm deployment.

---

## Verify Deployment

List the created bucket:

```bash
aws s3 ls
```

View bucket versioning:

```bash
aws s3api get-bucket-versioning \
  --bucket mlops-model-artifacts-prod
```

Expected output:

```json
{
  "Status": "Enabled"
}
```

---

## Lifecycle Management

The bucket automatically manages old model versions.

### Current Version

```text
model-v3.pkl
```

Stored in:

```text
S3 Standard
```

### Non-Current Versions

```text
model-v1.pkl
model-v2.pkl
```

After 60 days:

```text
Glacier Instant Retrieval
```

After 730 days:

```text
Automatically Deleted
```

This helps reduce storage costs while preserving rollback capability.

---

## Outputs

Terraform provides the following outputs:

### Bucket Name

```bash
terraform output bucket_name
```

### Bucket ARN

```bash
terraform output bucket_arn
```

---

## Example Usage

Upload a model artifact:

```bash
aws s3 cp model.pkl s3://mlops-model-artifacts-prod/
```

Upload a new version:

```bash
aws s3 cp model_v2.pkl s3://mlops-model-artifacts-prod/model.pkl
```

Because versioning is enabled, previous versions remain available.

---

## Security Controls

Implemented controls include:

* S3 Public Access Block
* Server-Side Encryption
* Versioning Protection
* Lifecycle Governance
* Infrastructure as Code

---

## Future Enhancements

Potential improvements for production environments:

* AWS KMS Encryption (SSE-KMS)
* Cross-Region Replication
* S3 Object Lock
* CloudTrail Data Events
* EventBridge Notifications
* Integration with MLflow
* CI/CD Deployment Pipeline
* Automated Compliance Checks

---

## Cleanup

To remove all infrastructure:

```bash
terraform destroy
```

Confirm with:

```text
yes
```

Terraform will delete all managed resources.

---

## Author

Created as an MLOps Infrastructure as Code demonstration using Terraform and AWS S3.

## License

MIT License
