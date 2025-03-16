# SRIP Portal Knative Deployment

## Architecture
![Service Architecture](service-architecture.png)

## Deployment Steps

```bash
kubectl get svc -n istio-system istio-ingressgateway -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
```