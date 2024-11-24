# AWS Kinesis Data Processing Project

## Overview
This project implements a serverless data processing pipeline using AWS Kinesis and Lambda. It includes functions for both producing and consuming data from Kinesis streams. The consumer function is setup for batch processing.

## Features
- Producer Lambda function for sending data to Kinesis
- Consumer Lambda function for processing stream events
- Historical data reader for batch processing
- Comprehensive unit tests
- Infrastructure as Code using Terraform
- Error handling and monitoring
- Configurable batch processing

## Project Structure

## Prerequisites
- AWS Account
- Python 3.8 or higher
- Terraform
- AWS CLI configured with appropriate credentials

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd kinesis
```
2. Create and activate a virtual env

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```
3. Install dependencies
```bash
pip install -r requirements.txt
```
4. Deploy infrastructure
```bash
cd terraform
terraform init
terraform apply
```

