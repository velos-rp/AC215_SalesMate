#!/bin/bash

echo "Container is running!!!"

# Authenticate AWS CLI using environment variables
aws configure set aws_access_key_id $AWS_ACCESS_KEY_ID
aws configure set aws_secret_access_key $AWS_SECRET_ACCESS_KEY
aws configure set default.region $AWS_REGION

/bin/bash
