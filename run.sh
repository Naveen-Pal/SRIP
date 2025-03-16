#!/bin/bash

# apply_knative.sh
# Applies all Knative YAML configurations in sequence

# Global configurations (apply first)
GLOBAL_FILES=(
    "knative/srip-secrets.yaml"
    # "knative/configmap.yaml"
)

# Service configurations (alphabetical order)
SERVICE_DIRS=(
    "auth"
    "coordinator" 
    "faculty"
    "home"
    "prospective_intern"
    "selected_intern"
)

# Cluster-wide configurations (apply last)
CLUSTER_FILES=(
    "knative/knative-routes.yaml"
)

echo "=== Applying global configurations ==="
for file in "${GLOBAL_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "Applying $file"
        kubectl apply -f "$file"
    else
        echo "Warning: Missing $file"
    fi
done

echo -e "\n=== Applying service configurations ==="
for service in "${SERVICE_DIRS[@]}"; do
    service_file="knative/${service}/service.yaml"
    if [ -f "$service_file" ]; then
        echo "Applying $service_file"
        kubectl apply -f "$service_file"
    else
        echo "Warning: Missing $service_file"
    fi
done

echo -e "\n=== Applying cluster configurations ==="
for file in "${CLUSTER_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "Applying $file"
        kubectl apply -f "$file"
    else
        echo "Warning: Missing $file"
    fi
done

echo -e "\n=== Deployment status ==="
kubectl get ksvc -o wide