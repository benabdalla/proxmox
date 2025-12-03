# Guide de Déploiement - Exemples

## Déploiements par Framework

### Django (Python)

#### Application Blog Django
```bash
curl -X POST http://localhost:5000/api/deploy \
  -H "Content-Type: application/json" \
  -d '{
    "type": "vm",
    "framework": "django",
    "github_url": "https://github.com/django/django-rest-framework.git",
    "name": "blog-django",
    "cpu": 2,
    "memory": 2048,
    "disk": 20
  }'
```

### Laravel (PHP)

#### Application E-commerce Laravel
```bash
curl -X POST http://localhost:5000/api/deploy \
  -H "Content-Type: application/json" \
  -d '{
    "type": "vm",
    "framework": "laravel",
    "github_url": "https://github.com/laravel/laravel.git",
    "name": "shop-laravel",
    "cpu": 2,
    "memory": 3072,
    "disk": 30
  }'
```

### Node.js/Express

#### API REST Node.js
```bash
curl -X POST http://localhost:5000/api/deploy \
  -H "Content-Type: application/json" \
  -d '{
    "type": "lxc",
    "framework": "nodejs",
    "github_url": "https://github.com/votre/api-nodejs.git",
    "name": "api-nodejs",
    "cpu": 2,
    "memory": 2048,
    "disk": 15
  }'
```

### React (Frontend)

#### Application React
```bash
curl -X POST http://localhost:5000/api/deploy \
  -H "Content-Type: application/json" \
  -d '{
    "type": "lxc",
    "framework": "react",
    "github_url": "https://github.com/facebook/create-react-app.git",
    "name": "frontend-react",
    "cpu": 1,
    "memory": 1024,
    "disk": 10
  }'
```

### Spring Boot (Java)

#### Microservice Spring Boot
```bash
curl -X POST http://localhost:5000/api/deploy \
  -H "Content-Type: application/json" \
  -d '{
    "type": "vm",
    "framework": "springboot",
    "github_url": "https://github.com/spring-projects/spring-boot.git",
    "name": "ms-springboot",
    "cpu": 4,
    "memory": 4096,
    "disk": 40
  }'
```

## Scénarios Complets

### Stack MEAN (MongoDB, Express, Angular, Node.js)

#### 1. Backend API
```bash
curl -X POST http://localhost:5000/api/deploy \
  -H "Content-Type: application/json" \
  -d '{
    "type": "vm",
    "framework": "nodejs",
    "github_url": "https://github.com/votre/mean-backend.git",
    "name": "mean-api",
    "cpu": 2,
    "memory": 2048,
    "disk": 20
  }'
```

#### 2. Frontend Angular
```bash
curl -X POST http://localhost:5000/api/deploy \
  -H "Content-Type: application/json" \
  -d '{
    "type": "lxc",
    "framework": "react",
    "github_url": "https://github.com/votre/mean-frontend.git",
    "name": "mean-frontend",
    "cpu": 1,
    "memory": 1024,
    "disk": 15
  }'
```

### Microservices Architecture

#### Service Utilisateurs (Django)
```bash
curl -X POST http://localhost:5000/api/deploy \
  -H "Content-Type: application/json" \
  -d '{
    "type": "lxc",
    "framework": "django",
    "github_url": "https://github.com/votre/users-service.git",
    "name": "ms-users",
    "cpu": 2,
    "memory": 2048,
    "disk": 15
  }'
```

#### Service Produits (Node.js)
```bash
curl -X POST http://localhost:5000/api/deploy \
  -H "Content-Type: application/json" \
  -d '{
    "type": "lxc",
    "framework": "nodejs",
    "github_url": "https://github.com/votre/products-service.git",
    "name": "ms-products",
    "cpu": 2,
    "memory": 1024,
    "disk": 15
  }'
```

#### Service Commandes (Spring Boot)
```bash
curl -X POST http://localhost:5000/api/deploy \
  -H "Content-Type: application/json" \
  -d '{
    "type": "vm",
    "framework": "springboot",
    "github_url": "https://github.com/votre/orders-service.git",
    "name": "ms-orders",
    "cpu": 3,
    "memory": 3072,
    "disk": 25
  }'
```

## Gestion des Déploiements

### Lister tous les déploiements
```bash
curl http://localhost:5000/api/deployments
```

### Obtenir les détails d'un déploiement
```bash
curl http://localhost:5000/api/deployments/1
```

### Voir les logs d'un déploiement
```bash
curl http://localhost:5000/api/deployments/1/logs
```

### Redémarrer un déploiement
```bash
curl -X POST http://localhost:5000/api/deployments/1/restart
```

### Supprimer un déploiement
```bash
curl -X DELETE http://localhost:5000/api/deployments/1
```

## Tests et Monitoring

### Vérifier le statut du système
```bash
curl http://localhost:5000/api/status | jq
```

### Afficher les ressources disponibles
```bash
curl http://localhost:5000/api/resources | jq
```

### Lister les frameworks supportés
```bash
curl http://localhost:5000/api/frameworks | jq
```

## Bonnes Pratiques

### Configuration des ressources

| Framework | Type | CPU | RAM (MB) | Disk (GB) |
|-----------|------|-----|----------|-----------|
| Django | VM | 2 | 2048 | 20 |
| Flask | LXC | 1 | 1024 | 10 |
| Laravel | VM | 2 | 3072 | 30 |
| Node.js | LXC | 2 | 2048 | 15 |
| React | LXC | 1 | 1024 | 10 |
| Spring Boot | VM | 4 | 4096 | 40 |

### Nommage des déploiements
- Utiliser des noms descriptifs
- Inclure le type d'application
- Ajouter l'environnement si applicable

Exemples:
- `api-users-prod`
- `frontend-shop-dev`
- `ms-payments-staging`

### Sécurité
- Toujours utiliser HTTPS pour les applications publiques
- Configurer les pare-feux appropriés
- Sauvegarder régulièrement les données
- Monitorer les ressources

## Automatisation avec Scripts

### Script de déploiement batch
```bash
#!/bin/bash

# deploy_multiple.sh
# Déploie plusieurs applications en parallèle

applications=(
    "vm django https://github.com/app1.git app1 2 2048 20"
    "lxc nodejs https://github.com/app2.git app2 2 1024 15"
    "vm laravel https://github.com/app3.git app3 2 3072 30"
)

for app in "${applications[@]}"; do
    read -r type framework url name cpu memory disk <<< "$app"
    
    curl -X POST http://localhost:5000/api/deploy \
      -H "Content-Type: application/json" \
      -d "{
        \"type\": \"$type\",
        \"framework\": \"$framework\",
        \"github_url\": \"$url\",
        \"name\": \"$name\",
        \"cpu\": $cpu,
        \"memory\": $memory,
        \"disk\": $disk
      }" &
done

wait
echo "Tous les déploiements ont été lancés!"
```

### Script de monitoring
```bash
#!/bin/bash

# monitor.sh
# Surveille l'état des déploiements

while true; do
    clear
    echo "=== Statut des déploiements ==="
    curl -s http://localhost:5000/api/status | jq
    echo ""
    echo "=== Déploiements actifs ==="
    curl -s http://localhost:5000/api/deployments | jq '.deployments[] | {id, name, status}'
    sleep 30
done
```
