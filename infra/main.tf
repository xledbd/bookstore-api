provider "aws" {
  region = "us-east-1"
}

resource "aws_dynamodb_table" "books_table" {
  name           = "Books"
  billing_mode   = "PROVISIONED"
  read_capacity  = 1
  write_capacity = 1
  hash_key       = "id"

  attribute {
    name = "id"
    type = "S"
  }
}

resource "aws_s3_bucket" "terraform_state" {
  bucket_prefix = "bookstore-"
}