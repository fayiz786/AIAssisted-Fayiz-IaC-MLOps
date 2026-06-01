# main.tf — AI-generated, manually reviewed

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  required_version = ">= 1.5.0"
}

provider "aws" {
  region = var.aws_region
}

# Variables
variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "bucket_name" {
  description = "S3 bucket name for model artifacts"
  type        = string
  default     = "mlops-model-artifacts-prod"
}

# S3 Bucket
resource "aws_s3_bucket" "model_artifacts" {
  bucket = var.bucket_name

  tags = {
    Environment = "production"
    Project     = "mlops-monitoring"
    ManagedBy   = "terraform"
  }
}

# Versioning — preserves model artifact history
resource "aws_s3_bucket_versioning" "model_artifacts" {
  bucket = aws_s3_bucket.model_artifacts.id

  versioning_configuration {
    status = "Enabled"
  }
}

# Server-side encryption at rest
resource "aws_s3_bucket_server_side_encryption_configuration" "model_artifacts" {
  bucket = aws_s3_bucket.model_artifacts.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Block all public access
resource "aws_s3_bucket_public_access_block" "model_artifacts" {
  bucket = aws_s3_bucket.model_artifacts.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Lifecycle Management
# Move old/non-current model versions to Glacier Instant Retrieval
# and delete them after 2 years
resource "aws_s3_bucket_lifecycle_configuration" "model_artifacts" {
  bucket = aws_s3_bucket.model_artifacts.id

  rule {
    id     = "ml-model-version-lifecycle"
    status = "Enabled"

    filter {
      prefix = ""
    }

    noncurrent_version_transition {
      noncurrent_days = 60
      storage_class   = "GLACIER_IR"
    }

    noncurrent_version_expiration {
      noncurrent_days = 730
    }
  }

  depends_on = [
    aws_s3_bucket_versioning.model_artifacts
  ]
}

# Outputs
output "bucket_arn" {
  description = "ARN of the model artifacts bucket"
  value       = aws_s3_bucket.model_artifacts.arn
}

output "bucket_name" {
  description = "Name of the model artifacts bucket"
  value       = aws_s3_bucket.model_artifacts.bucket
}