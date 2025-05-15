output "dynamodb_table_name" {
  value       = aws_dynamodb_table.books_table.name
  description = "The name of the DynamoDB table"
}

output "dynamodb_table_arn" {
  value       = aws_dynamodb_table.books_table.arn
  description = "The ARN of the DynamoDB table"
}

output "terraform_state_bucket" {
  value       = aws_s3_bucket.terraform_state.bucket
  description = "The name of the S3 bucket for Terraform state"
}