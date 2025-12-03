# API Documentation

## Base URL
```
http://localhost:5000/api
```

## Endpoints

### 1. Créer un déploiement

**POST** `/deploy`

Crée un nouveau déploiement d'application.

#### Request Body
```json
{
  "type": "vm|lxc",
  "framework": "django|laravel|nodejs|...",
  "github_url": "https://github.com/user/repo.git",
  "name": "optional-name",
  "cpu": 2,
  "memory": 2048,
  "disk": 20
}
```

#### Response (202 Accepted)
```json
{
  "message": "Déploiement démarré",
  "deployment": {
    "id": 1,
    "name": "django-20231203-143022",
    "type": "vm",
    "framework": "django",
    "github_url": "https://github.com/user/repo.git",
    "resources": {
      "cpu": 2,
      "memory": 2048,
      "disk": 20
    },
    "status": "pending",
    "created_at": "2023-12-03T14:30:22.123456"
  }
}
```

#### Erreurs possibles
- `400 Bad Request` - Données invalides
- `500 Internal Server Error` - Erreur serveur

---

### 2. Lister les déploiements

**GET** `/deployments`

Récupère la liste de tous les déploiements.

#### Response (200 OK)
```json
{
  "deployments": [
    {
      "id": 1,
      "name": "django-app",
      "type": "vm",
      "framework": "django",
      "status": "running",
      "proxmox": {
        "id": 100,
        "node": "pve",
        "ip": "192.168.1.150"
      },
      "created_at": "2023-12-03T14:30:22.123456"
    }
  ],
  "total": 1
}
```

---

### 3. Obtenir un déploiement

**GET** `/deployments/{id}`

Récupère les détails d'un déploiement spécifique.

#### Response (200 OK)
```json
{
  "id": 1,
  "name": "django-app",
  "type": "vm",
  "framework": "django",
  "github_url": "https://github.com/user/repo.git",
  "resources": {
    "cpu": 2,
    "memory": 2048,
    "disk": 20
  },
  "proxmox": {
    "id": 100,
    "node": "pve",
    "ip": "192.168.1.150"
  },
  "status": "running",
  "created_at": "2023-12-03T14:30:22.123456",
  "deployed_at": "2023-12-03T14:45:30.123456"
}
```

#### Erreurs possibles
- `404 Not Found` - Déploiement introuvable

---

### 4. Supprimer un déploiement

**DELETE** `/deployments/{id}`

Supprime un déploiement et détruit son infrastructure.

#### Response (200 OK)
```json
{
  "message": "Déploiement supprimé",
  "deployment_id": 1
}
```

#### Erreurs possibles
- `404 Not Found` - Déploiement introuvable
- `500 Internal Server Error` - Erreur lors de la destruction

---

### 5. Obtenir les logs

**GET** `/deployments/{id}/logs`

Récupère les logs d'un déploiement.

#### Response (200 OK)
```json
{
  "deployment_id": 1,
  "terraform_output": "...",
  "deployment_log": "..."
}
```

---

### 6. Redémarrer un déploiement

**POST** `/deployments/{id}/restart`

Redémarre la VM/conteneur d'un déploiement.

#### Response (200 OK)
```json
{
  "message": "Déploiement redémarré",
  "deployment_id": 1
}
```

---

### 7. Statut du système

**GET** `/status`

Récupère le statut global du système.

#### Response (200 OK)
```json
{
  "system": {
    "status": "operational",
    "proxmox_connected": true
  },
  "deployments": {
    "total": 10,
    "running": 8,
    "failed": 1,
    "pending": 1
  }
}
```

---

### 8. Liste des frameworks

**GET** `/frameworks`

Récupère la liste des frameworks supportés.

#### Response (200 OK)
```json
{
  "python": [
    {
      "id": "django",
      "name": "Django",
      "version": "4.x"
    }
  ],
  "javascript": [...],
  "php": [...],
  "java": [...]
}
```

---

### 9. Ressources Proxmox

**GET** `/resources`

Récupère les ressources disponibles sur Proxmox.

#### Response (200 OK)
```json
{
  "node": {
    "name": "pve",
    "status": "online",
    "cpu": {
      "cores": 8,
      "usage": 25.5
    },
    "memory": {
      "total": 32.0,
      "used": 12.5,
      "free": 19.5
    }
  },
  "vms": {
    "total": 5,
    "running": 4
  },
  "containers": {
    "total": 3,
    "running": 2
  }
}
```

---

## Codes de statut des déploiements

| Statut | Description |
|--------|-------------|
| `pending` | En attente de traitement |
| `creating` | Infrastructure en cours de création |
| `running` | Déploiement actif et fonctionnel |
| `failed` | Déploiement échoué |
| `stopped` | Déploiement arrêté |
| `deleted` | Déploiement supprimé |

## Exemples cURL

### Créer un déploiement Django
```bash
curl -X POST http://localhost:5000/api/deploy \
  -H "Content-Type: application/json" \
  -d '{
    "type": "vm",
    "framework": "django",
    "github_url": "https://github.com/user/django-app.git",
    "cpu": 2,
    "memory": 2048,
    "disk": 20
  }'
```

### Lister les déploiements
```bash
curl http://localhost:5000/api/deployments
```

### Supprimer un déploiement
```bash
curl -X DELETE http://localhost:5000/api/deployments/1
```

## Exemples Python

```python
import requests

API_URL = "http://localhost:5000/api"

# Créer un déploiement
response = requests.post(f"{API_URL}/deploy", json={
    "type": "vm",
    "framework": "django",
    "github_url": "https://github.com/user/repo.git",
    "cpu": 2,
    "memory": 2048,
    "disk": 20
})

deployment = response.json()
print(f"Déploiement créé: {deployment['deployment']['id']}")

# Vérifier le statut
deployment_id = deployment['deployment']['id']
response = requests.get(f"{API_URL}/deployments/{deployment_id}")
status = response.json()
print(f"Statut: {status['status']}")
```

## Exemples JavaScript

```javascript
const API_URL = 'http://localhost:5000/api';

// Créer un déploiement
async function createDeployment() {
  const response = await fetch(`${API_URL}/deploy`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      type: 'vm',
      framework: 'nodejs',
      github_url: 'https://github.com/user/repo.git',
      cpu: 2,
      memory: 2048,
      disk: 20
    })
  });
  
  const data = await response.json();
  console.log('Déploiement créé:', data.deployment.id);
  return data.deployment.id;
}

// Lister les déploiements
async function listDeployments() {
  const response = await fetch(`${API_URL}/deployments`);
  const data = await response.json();
  console.log('Déploiements:', data.deployments);
}
```
