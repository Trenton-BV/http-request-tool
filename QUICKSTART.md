# Quick Start Guide

## Lokaal Testen

```bash
# Build en start de applicatie
docker compose up -d

# Check logs
docker compose logs -f

# Open in browser
open http://localhost:8080
```

**Data persistentie**: De history database wordt opgeslagen in `./data/history.db` en blijft behouden tussen container restarts.

## Kubernetes Deployment

### Optie 1: Automatisch (aanbevolen)

```bash
./build-and-deploy.sh
```

### Optie 2: Manueel

```bash
# 1. Build image
docker build -t http-request-tool:latest .

# 2. Deploy naar K8s
kubectl apply -f k8s/

# 3. Port forward
kubectl port-forward svc/http-request-tool 8080:8000

# 4. Open browser
open http://localhost:8080
```

## Gebruik Binnen K8s

Eenmaal gedeployed in je K8s cluster, kun je deze tool gebruiken om requests te maken naar andere services:

### Voorbeeld 1: Service in dezelfde namespace
```
URL: http://my-service:8080/api/endpoint
```

### Voorbeeld 2: Service in andere namespace
```
URL: http://my-service.other-namespace.svc.cluster.local:8080/api/endpoint
```

### Voorbeeld 3: POST request met JSON body
```
Method: POST
URL: http://api-service:3000/users
Headers: {"Content-Type": "application/json"}
Body: {"name": "Test User", "email": "test@example.com"}
```

## Handige Commando's

```bash
# Check status
kubectl get pods -l app=http-request-tool
kubectl get svc http-request-tool

# View logs
kubectl logs -l app=http-request-tool -f

# Restart pod
kubectl rollout restart deployment/http-request-tool

# Delete deployment
kubectl delete -f k8s/

# Stop lokale container
docker compose down
```

## Troubleshooting

### Container start niet
```bash
docker compose logs
```

### Kan service niet bereiken in K8s
1. Check of de target service draait: `kubectl get pods`
2. Check service naam: `kubectl get svc`
3. Test DNS: `kubectl exec -it <http-tool-pod> -- nslookup my-service`
4. Check network policies: `kubectl get networkpolicies`

### Port al in gebruik (lokaal)
Wijzig de poort in `docker-compose.yml`:
```yaml
ports:
  - "8081:8000"  # Gebruik 8081 in plaats van 8080
```
