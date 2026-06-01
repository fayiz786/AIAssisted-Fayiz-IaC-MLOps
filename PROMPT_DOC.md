# PROMPT_DOC.md

# Terraform Execution Guide

This document explains how to execute and validate the Terraform configuration contained in `main.tf`.

---

## Purpose

The Terraform configuration provisions an AWS S3 bucket intended for storing Machine Learning model artifacts with:

* Versioning enabled
* Server-side encryption
* Public access blocked
* Lifecycle management for old model versions

---

## Prerequisites

### Install Terraform

Verify installation:

```bash
terraform -version
```

Expected:

```text
Terraform v1.5+
```

---

### Install AWS CLI

Verify installation:

```bash
aws --version
```

---

### Configure AWS Credentials

Configure AWS access:

```bash
aws configure
```

Provide:

```text
AWS Access Key ID
AWS Secret Access Key
Default region
Output format
```

Verify access:

```bash
aws sts get-caller-identity
```

---

## Initialize Terraform

Download required providers:

```bash
terraform init
```

Expected output:

```text
Terraform has been successfully initialized!
```

---

## Validate Configuration

Check Terraform syntax:

```bash
terraform validate
```

Expected:

```text
Success! The configuration is valid.
```

---

## Review Execution Plan

Generate deployment plan:

```bash
terraform plan
```

Terraform will display resources to be created:

```text
+ aws_s3_bucket.model_artifacts
+ aws_s3_bucket_versioning.model_artifacts
+ aws_s3_bucket_lifecycle_configuration.model_artifacts
```

---

## Deploy Resources

Create infrastructure:

```bash
terraform apply
```

Confirm:

```text
yes
```

Expected:

```text
Apply complete!
```

---

## Verify S3 Bucket

List available buckets:

```bash
aws s3 ls
```

Verify bucket exists:

```bash
aws s3api head-bucket \
  --bucket mlops-model-artifacts-prod
```

---

## Verify Versioning

```bash
aws s3api get-bucket-versioning \
  --bucket mlops-model-artifacts-prod
```

Expected:

```json
{
  "Status": "Enabled"
}
```

---

## Verify Encryption

```bash
aws s3api get-bucket-encryption \
  --bucket mlops-model-artifacts-prod
```

Expected:

```json
{
  "ServerSideEncryptionConfiguration": {
    ...
  }
}
```

---

## Test Versioning

Create a sample file:

```bash
echo "Model Version 1" > model.txt
```

Upload:

```bash
aws s3 cp model.txt s3://mlops-model-artifacts-prod/
```

Modify file:

```bash
echo "Model Version 2" > model.txt
```

Upload again:

```bash
aws s3 cp model.txt s3://mlops-model-artifacts-prod/
```

Check versions:

```bash
aws s3api list-object-versions \
  --bucket mlops-model-artifacts-prod
```

Multiple versions should be visible.

---

## Terraform Outputs

View bucket name:

```bash
terraform output bucket_name
```

View bucket ARN:

```bash
terraform output bucket_arn
```

---

## Destroy Resources

Remove all resources:

```bash
terraform destroy
```

Confirm:

```text
yes
```

Expected:

```text
Destroy complete!
```

---

## Troubleshooting

### Provider Download Failure

Re-run:

```bash
terraform init -upgrade
```

### AWS Authentication Error

Verify credentials:

```bash
aws sts get-caller-identity
```

### Bucket Name Already Exists

Update:

```hcl
bucket_name = "unique-bucket-name"
```

S3 bucket names must be globally unique.

---

## Expected Learning Outcomes

After completing this exercise, you will understand:

* Terraform workflow (init, plan, apply, destroy)
* AWS S3 provisioning
* S3 Versioning
* Lifecycle Policies
* Infrastructure as Code (IaC)
* Cloud resource management using Terraform



## Two-Line Reflection
What the AI got right: It correctly scaffolded the Terraform provider block, variable declarations, tagging conventions, and the full PSI drift detection logic with zero hallucinated resource names.

What I had to correct manually: The initial Terraform output used nested versioning {} and server_side_encryption_configuration {} blocks inside aws_s3_bucket — a pattern removed in AWS provider v5 — requiring a split into three separate child resources.



