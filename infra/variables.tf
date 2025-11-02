# infra/variables.tf
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "eu-west-2"
}

variable "app_name" {
  description = "Name of the application"
  type        = string
  default     = "rfp-copilot"
}

variable "container_port" {
  description = "Port the container listens on"
  type        = number
  default     = 8501
}

variable "domain_name" {
  description = "Custom domain (optional)"
  type        = string
  default     = ""
}

# infra/variables.tf (add)
variable "openai_api_key" {
  description = "OpenAI API Key"
  type        = string
  sensitive   = true
}

variable "certificate_arn" {
  description = "ACM Certificate ARN for HTTPS"
  type        = string
  default     = ""  # Use AWS Certificate Manager
}