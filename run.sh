#!/bin/bash

# apply_knative.sh
# Applies or deletes all Knative YAML configurations

# Configuration files
GLOBAL_FILES=(
    "knative/srip-secrets.yaml"
)
SERVICE_DIRS=(
    "auth"
    "coordinator" 
    "faculty"
    "home"
    "prospective_intern"
    "selected_intern"
)
CLUSTER_FILES=(
    # "knative/routes.yaml"
    # "knative/config-domain.yaml"
)

apply_resources() {
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
}

delete_resources() {
    echo "=== Deleting cluster configurations ==="
    for file in "${CLUSTER_FILES[@]}"; do
        if [ -f "$file" ]; then
            echo "Deleting $file"
            kubectl delete -f "$file"
        fi
    done

    echo -e "\n=== Deleting service configurations ==="
    for service in "${SERVICE_DIRS[@]}"; do
        service_file="knative/${service}/service.yaml"
        if [ -f "$service_file" ]; then
            echo "Deleting $service_file"
            kubectl delete -f "$service_file"
        fi
    done

    echo -e "\n=== Deleting global configurations ==="
    for file in "${GLOBAL_FILES[@]}"; do
        if [ -f "$file" ]; then
            echo "Deleting $file"
            kubectl delete -f "$file"
        fi
    done

    echo -e "\n=== Remaining services ==="
    kubectl get ksvc -o wide
}

case "$1" in
    --delete|-d)
        delete_resources
        ;;
    --help|-h)
        echo "Usage: $0 [OPTION]"
        echo "Apply or delete Knative configurations"
        echo -e "\nOptions:"
        echo "  (no option)     Apply configurations"
        echo "  -d, --delete    Delete configurations"
        echo "  -h, --help      Show this help"
        ;;
    *)
        apply_resources
        ;;
esac