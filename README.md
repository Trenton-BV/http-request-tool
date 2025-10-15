# HTTP Request Tool

Een Python-gebaseerde HTTP request tool met FastAPI backend en web frontend. Perfect voor het testen van API endpoints binnen Kubernetes clusters.

## Features

- ✅ Ondersteunt alle HTTP methods (GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS)
- ✅ Custom headers configuratie
- ✅ JSON body support
- ✅ Mooie web interface met Tailwind CSS
- ✅ Response weergave met syntax highlighting
- ✅ **SQLite database voor request history**
- ✅ **Configureerbaar storage pad voor persistent data**
- ✅ **History browser met search en replay functionaliteit**
- ✅ **Request duration tracking**
- ✅ Docker en Kubernetes ready met persistent volumes

## Lokaal Draaien

### Met Docker Compose

```bash
docker compose build
docker compose up
```

De applicatie is beschikbaar op: http://localhost:8000

### Zonder Docker

```bash
cd app
pip install -r requirements.txt
python main.py
```

## Configuratie

### Database Path

Het pad waar de SQLite database wordt opgeslagen is configureerbaar via de `DB_PATH` environment variable:

- **Default**: `/data/history.db`
- **Docker Compose**: Gemount naar `./data/history.db` (lokale directory)
- **Kubernetes**: Persistent Volume via PVC

```bash
# Custom pad instellen
export DB_PATH=/custom/path/history.db
```

## Kubernetes Deployment

### 1. Build de Docker image (optioneel - gebeurt automatisch via GitHub Actions)

```bash
docker build -t ghcr.io/trenton-bv/http-request-tool:latest .
```

### 2. Deploy naar Kubernetes

```bash
# Alle manifests tegelijk deployen (inclusief PVC)
kubectl apply -f k8s/

# Of individueel
kubectl apply -f k8s/pvc.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml
```

**Let op**: De deployment gebruikt een PersistentVolumeClaim voor data persistentie. De history database blijft behouden bij pod restarts.

### 3. Controleer de deployment

```bash
# Check pods
kubectl get pods -l app=http-request-tool

# Check service
kubectl get svc http-request-tool

# Check logs
kubectl logs -l app=http-request-tool -f
```

### 4. Toegang tot de applicatie

**Via Port Forward:**
```bash
kubectl port-forward svc/http-request-tool 8000:8000
```

Dan open: http://localhost:8000

**Via Ingress:**
Als je een ingress controller hebt (bijv. nginx-ingress):
```bash
# Voeg toe aan /etc/hosts
echo "127.0.0.1 http-request-tool.local" | sudo tee -a /etc/hosts
```

Dan open: http://http-request-tool.local

## Gebruik

### Request maken

1. Open de web interface
2. Selecteer HTTP method (GET, POST, etc.)
3. Voer de URL in van de service die je wilt testen
   - Bijvoorbeeld: `http://my-service:8080/api/endpoint`
   - Of: `http://my-service.namespace.svc.cluster.local:8080/api/endpoint`
4. Voeg optioneel headers toe (JSON format)
5. Voeg optioneel een body toe (JSON format) voor POST/PUT/PATCH
6. Klik op "Send" of druk Ctrl+Enter
7. Bekijk de response met status code, headers, body en duration

### History gebruiken

1. Klik op "Show History" om alle vorige requests te zien
2. Klik op een history item om het te laden in het formulier
3. Pas aan indien nodig en verstuur opnieuw
4. Verwijder individuele items met de × knop
5. Clear alle history met "Clear All"

Alle requests worden automatisch opgeslagen in de SQLite database met:
- Timestamp
- Method, URL, headers en body
- Response status, headers en body
- Request duration in milliseconds
- Error messages (indien van toepassing)

## Voorbeelden

### GET Request
```
Method: GET
URL: http://my-api-service:8080/users
Headers: {"Authorization": "Bearer token123"}
```

### POST Request
```
Method: POST
URL: http://my-api-service:8080/users
Headers: {"Content-Type": "application/json"}
Body: {"name": "John", "email": "john@example.com"}
```

### DELETE Request
```
Method: DELETE
URL: http://my-api-service:8080/users/123
Headers: {"Authorization": "Bearer token123"}
```

## API Endpoint

De tool heeft ook een programmatische API:

```bash
curl -X POST http://localhost:8000/api/request \
  -H "Content-Type: application/json" \
  -d '{
    "method": "GET",
    "url": "http://example.com/api",
    "headers": {"Authorization": "Bearer token"},
    "body": {}
  }'
```

## Troubleshooting

### Container start niet
```bash
# Check logs
docker compose logs -f

# Of in Kubernetes
kubectl logs -l app=http-request-tool
```

### Kan andere services niet bereiken in K8s
Zorg ervoor dat:
- De service naam correct is
- De namespace correct is (gebruik FQDN: `service.namespace.svc.cluster.local`)
- Network policies geen verkeer blokkeren
- De target service draait en bereikbaar is

### SSL/TLS errors
De tool gebruikt `verify=False` voor HTTPS requests om self-signed certificates te accepteren binnen K8s clusters.

## Structuur

```
.
├── app/
│   ├── main.py              # FastAPI backend
│   ├── requirements.txt     # Python dependencies
│   └── templates/
│       └── index.html       # Web frontend
├── k8s/
│   ├── deployment.yaml      # K8s deployment
│   ├── service.yaml         # K8s service
│   └── ingress.yaml         # K8s ingress (optioneel)
├── Dockerfile               # Container image
├── docker-compose.yml       # Lokale development
└── README.md               # Deze file
```

## Licentie

MIT
