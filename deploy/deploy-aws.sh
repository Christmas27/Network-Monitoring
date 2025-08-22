#!/bin/bash
# AWS ECS Deployment Script

echo "🚀 Deploying Network Dashboard to AWS ECS..."

# Configuration
CLUSTER_NAME="network-dashboard-cluster"
SERVICE_NAME="network-dashboard-service"
TASK_DEFINITION="network-dashboard"
IMAGE_NAME="ghcr.io/christmas27/network-monitoring:latest"

# Check if AWS CLI is installed and configured
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not found. Please install and configure it first."
    exit 1
fi

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS credentials not configured. Run 'aws configure' first."
    exit 1
fi

echo "Creating ECS cluster..."
aws ecs create-cluster --cluster-name $CLUSTER_NAME

echo "Registering task definition..."
aws ecs register-task-definition --cli-input-json file://deploy/ecs-task-definition.json

echo "Creating ECS service..."
aws ecs create-service \
    --cluster $CLUSTER_NAME \
    --service-name $SERVICE_NAME \
    --task-definition $TASK_DEFINITION \
    --desired-count 1 \
    --launch-type FARGATE \
    --network-configuration "awsvpcConfiguration={subnets=[subnet-12345678],securityGroups=[sg-12345678],assignPublicIp=ENABLED}"

echo "✅ Deployment initiated!"
echo "🔍 Monitor deployment: aws ecs describe-services --cluster $CLUSTER_NAME --services $SERVICE_NAME"
