output "s3-bucket-url" {
    value = module.s3_web_bucket.s3_bucket_website_endpoint
    description = "Url for the s3 bucket containing frontend bundle"
}