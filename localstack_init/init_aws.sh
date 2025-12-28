#!/bin/bash
echo "Initializing LocalStack..."

# Create a default S3 bucket for the application
awslocal s3 mb s3://secure-rag-data

echo "LocalStack initialized!"
