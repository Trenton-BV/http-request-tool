#!/bin/bash

# Build and Deploy script voor HTTP Request Tool

set -e

echo "🔨 Building Docker image..."
docker build -t http-request-tool:latest .

echo "✅ Docker image built successfully!"
echo ""
echo "📦 Deploying to Kubernetes..."
kubectl apply -f k8s/

echo ""
echo "⏳ Waiting for deployment to be ready..."
kubectl wait --for=condition=available --timeout=60s deployment/http-request-tool

echo ""
echo "✅ Deployment successful!"
echo ""
echo "📊 Current status:"
kubectl get pods -l app=http-request-tool
kubectl get svc http-request-tool

echo ""
echo "🌐 To access the application:"
echo "   kubectl port-forward svc/http-request-tool 8000:8000"
echo ""
echo "   Then open: http://localhost:8000"
