locals {
  known_thumbprints = [
    "1c58a3a8518e8759bf075b76b750d4f2df264fcd",
    "6938fd4d98bab03faadb97b34396831e3780aea1",
    "1b511abead59c6ce207077c0bf0e0043b1382612"
  ]
  release_branch = coalesce(var.release_branch, data.github_repository.repo.default_branch)
}

data "github_repository" "repo" {
  name  = var.repo_name
}

output "data_github_repo" {
  value = data.github_repository.repo
}

resource "aws_iam_openid_connect_provider" "github_oidc" {
  url             = "https://token.actions.githubusercontent.com"
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = local.known_thumbprints
}

data "aws_iam_policy_document" "github_oidc" {
  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]
    effect  = "Allow"

    principals {
      type        = "Federated"
      identifiers = [resource.aws_iam_openid_connect_provider.github_oidc.arn]
    }

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"

      values = ["sts.amazonaws.com"]
    }

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:sub"

      values = ["repo:${data.github_repository.repo.full_name}:ref:refs/heads/${local.release_branch}"]
    }
  }
}

resource "aws_iam_role" "web_pipeline" {
  name = "WEB-Pipeline-Role"
  inline_policy {
    name = "AllowWebResources"
    policy = jsonencode({
      Version = "2012-10-17"
      Statement = [
        {
          Effect = "Allow"
          Action = "s3:*"
          Resource = [
            module.s3_web_bucket.s3_bucket_arn,
            "${module.s3_web_bucket.s3_bucket_arn}/*"
          ]
        }
      ]
    })
  }
  assume_role_policy = data.aws_iam_policy_document.github_oidc.json
}

resource "local_file" "github_action" {
  content = templatefile("${path.module}/templates/deployToS3.yml.tpl",
    {
      ASSUME_ROLE           = resource.aws_iam_role.web_pipeline.arn
      AWS_REGION            = var.aws_region
      RELEASE_BRANCH        = local.release_branch
      VITE_SUPABASE_API_KEY = var.supabase_key
      VITE_SUPABASE_API_URL = var.supabase_url
      WEB_BUCKET            = local.bucket_name
  })
  filename = "../.github/workflows/deployToS3.yml"
}
