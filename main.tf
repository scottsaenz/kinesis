provider "aws" {
  region = var.aws_region
}

# Create Kinesis Data Stream
resource "aws_kinesis_stream" "data_stream" {
  name             = "example-stream"
  shard_count      = 1
  retention_period = 24

  stream_mode_details {
    stream_mode = "PROVISIONED"
  }
}

# Producer Lambda Function
resource "aws_lambda_function" "producer" {
  filename         = data.archive_file.producer_lambda.output_path
  function_name    = "kinesis-producer"
  role            = aws_iam_role.producer_role.arn
  handler         = "lambda_function.lambda_handler"
  runtime         = "python3.9"

  environment {
    variables = {
      STREAM_NAME = aws_kinesis_stream.data_stream.name
    }
  }
}

# Consumer Lambda Function
resource "aws_lambda_function" "consumer" {
  filename         = data.archive_file.consumer_lambda.output_path
  function_name    = "kinesis-consumer"
  role            = aws_iam_role.consumer_role.arn
  handler         = "lambda_function.lambda_handler"
  runtime         = "python3.9"
}

# Create Lambda Event Source Mapping
resource "aws_lambda_event_source_mapping" "kinesis_trigger" {
  event_source_arn  = aws_kinesis_stream.data_stream.arn
  function_name     = aws_lambda_function.consumer.arn
  starting_position = "LATEST"
}

# Archive files for Lambda functions
data "archive_file" "producer_lambda" {
  type        = "zip"
  source_file = "${path.module}/src/producer/put_kinesis.py"
  output_path = "${path.module}/put_kinesis.zip"
}

data "archive_file" "consumer_lambda" {
  type        = "zip"
  source_file = "${path.module}/src/consumer/read_kinesis.py"
  output_path = "${path.module}/read_kinesis.zip"
}
