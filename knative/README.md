# SRIP Portal Knative Deployment

## Architecture
![Service Architecture](service-architecture.png)

## Deployment Steps

1. Build and push Docker images:
```bash
export DOCKER_USER=naveen-pal
SERVICES=(auth coordinator faculty intern home)

for service in "${SERVICES[@]}"; do
  docker build -t $DOCKER_USER/$service-service -f services/$service/Dockerfile .
  docker push $DOCKER_USER/$service-service
done