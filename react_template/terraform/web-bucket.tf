locals {
  bucket_name = "${var.project_name}-webapp-${resource.random_string.bucket_id.id}"
}

resource "random_string" "bucket_id" {
  length = 8
  upper = false
  special = false
}

# Creates an s3 Bucket
module "s3_web_bucket" {
  source  = "terraform-aws-modules/s3-bucket/aws"
  version = "3.15.1"

  bucket        = local.bucket_name
  force_destroy = false

  versioning = {
    enabled = false
  }

  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
  block_public_acls       = false
  attach_policy           = true
  policy = jsonencode({
    "Version" = "2012-10-17"
    "Statement" = [
      {
        "Sid"       = "PublicReadGetObject"
        "Effect"    = "Allow"
        "Principal" = "*"
        "Action" = [
          "s3:GetObject"
        ]
        "Resource" = [
          "arn:aws:s3:::${local.bucket_name}/*"
        ]
      }
    ]
  })

  cors_rule = [
    {
      allowed_headers = [
        "*"
      ]
      allowed_methods = [
        "GET",
      ]
      allowed_origins = [
        "*"
      ]
    }
  ]

  website = {
    index_document = "index.html"
    error_document = "index.html"
  }
}

resource "null_resource" "web_build_and_deploy" {
  provisioner "local-exec" {
    command     = "npm install && npm run build"
    working_dir = "${path.module}/.."
    environment = {
      VITE_SUPABASE_API_KEY = var.supabase_key
      VITE_SUPABASE_API_URL = var.supabase_url
    }
  }

  provisioner "local-exec" {
    command     = "aws s3 sync dist s3://${local.bucket_name} --delete"
    working_dir = "${path.module}/.."
  }

  triggers = {
    on_new_bucket = coalesce(module.s3_web_bucket.s3_bucket_id, "")
  }
}
