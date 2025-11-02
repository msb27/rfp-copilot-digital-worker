# infra/backend.tf
terraform {
  backend "s3" {
    bucket         = "tf-state-rfp-copilot"  # Create this bucket manually
    key            = "ecs/terraform.tfstate"
    region         = "eu-west-2"
    dynamodb_table = "tf-lock-rfp-copilot"  # Create this table manually
    encrypt        = true
  }
}