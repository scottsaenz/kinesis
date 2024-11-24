output "kinesis_stream_name" {
  value = aws_kinesis_stream.data_stream.name
}

output "producer_function_name" {
  value = aws_lambda_function.producer.function_name
}

output "consumer_function_name" {
  value = aws_lambda_function.consumer.function_name
}
