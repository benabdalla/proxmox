# Architecture de la Plateforme PaaS

## Vue d'ensemble

```
┌─────────────────────────────────────────────────────────────┐
│                      UTILISATEUR                            │
│                    (Navigateur Web)                         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  INTERFACE WEB (Frontend)                   │
│  ┌──────────┬──────────┬──────────┬──────────┐             │
│  │ Dashboard│ Formulaire│  Liste  │Ressources│             │
│  │          │  Déploie  │ Déploie │ Proxmox  │             │
│  └──────────┴──────────┴──────────┴──────────┘             │
│              HTML + CSS + JavaScript                        │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP REST API
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  BACKEND API (Flask)                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Routes API                              │  │
│  │  /deploy  /deployments  /status  /resources         │  │
│  └────────┬─────────────────────────────────────────────┘  │
│           │                                                 │
│  ┌────────▼──────────┬─────────────────┬─────────────────┐ │
│  │  Deployment       │   Proxmox       │   Terraform     │ │
│  │  Service          │   Service       │   Service       │ │
│  │                   │                 │                 │ │
│  │ - Orchestration   │ - API Client    │ - Config Gen    │ │
│  │ - Validation      │ - VM Control    │ - Apply/Destroy │ │
│  │ - Logs            │ - Monitoring    │ - State Mgmt    │ │
│  └───────────────────┴─────────────────┴─────────────────┘ │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           Base de données SQLite                     │  │
│  │  - Déploiements  - Logs  - États                    │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
┌───────────────────┐    ┌────────────────────┐
│    TERRAFORM      │    │   PROXMOX API      │
│                   │    │                    │
│  - .tf files      │    │  - VM Management   │
│  - State files    │    │  - LXC Management  │
│  - Variables      │    │  - Resources       │
└────────┬──────────┘    └─────────┬──────────┘
         │                         │
         └────────────┬────────────┘
                      ▼
         ┌─────────────────────────┐
         │   PROXMOX VE CLUSTER    │
         │                         │
         │  ┌──────┬──────┬──────┐ │
         │  │ VM 1 │ VM 2 │ LXC 1│ │
         │  │Django│Laravel│Node │ │
         │  └──────┴──────┴──────┘ │
         └─────────────────────────┘
```

## Composants Détaillés

### 1. Frontend (Interface Web)

**Technologies:**
- HTML5 / CSS3
- JavaScript (Vanilla)
- Font Awesome (icônes)

**Fonctionnalités:**
- Formulaire de déploiement interactif
- Tableau de bord des déploiements
- Visualisation des ressources
- Notifications en temps réel
- Interface responsive

**Fichiers:**
```
frontend/
├── index.html          # Page principale
├── css/
│   └── style.css      # Styles
└── js/
    └── app.js         # Logique client
```

---

### 2. Backend API (Flask)

**Technologies:**
- Python 3.8+
- Flask (Web framework)
- SQLAlchemy (ORM)
- Proxmoxer (API Proxmox)
- python-terraform (Wrapper Terraform)

**Architecture:**

```
backend/
├── app.py                    # Application principale
├── models/
│   └── database.py          # Modèles de données
├── api/
│   ├── deployment.py        # Routes déploiement
│   └── status.py           # Routes statut
├── services/
│   ├── deployment_service.py  # Logique déploiement
│   ├── terraform_service.py   # Gestion Terraform
│   └── proxmox_service.py     # Client Proxmox
└── utils/
    ├── config.py             # Configuration
    ├── validators.py         # Validation
    └── script_generator.py   # Génération scripts
```

**Services:**

#### DeploymentService
- Orchestration du processus de déploiement
- Gestion asynchrone des tâches
- Logging et gestion d'erreurs

#### TerraformService
- Génération dynamique de fichiers .tf
- Initialisation et application Terraform
- Gestion des états et outputs

#### ProxmoxService
- Communication avec l'API Proxmox
- Contrôle des VMs et conteneurs
- Récupération des ressources

---

### 3. Terraform

**Rôle:**
- Infrastructure as Code
- Provisionnement automatique
- Gestion de l'état

**Flux de travail:**

```
1. Génération configuration (.tf files)
   ↓
2. terraform init
   ↓
3. terraform apply
   ↓
4. Création VM/LXC sur Proxmox
   ↓
5. Récupération des outputs (IP, ID)
```

**Fichiers générés:**
```
terraform/workspaces/deployment-{id}/
├── main.tf          # Ressources Proxmox
├── variables.tf     # Variables
└── terraform.tfvars # Valeurs
```

---

### 4. Proxmox VE

**Rôle:**
- Hyperviseur de virtualisation
- Gestion des VMs (QEMU/KVM)
- Gestion des conteneurs (LXC)

**Interactions:**
- API REST (JSON)
- Authentification par token
- Contrôle des ressources

---

### 5. Scripts d'installation

**install_framework.sh**
- Installation des dépendances système
- Configuration du langage/runtime
- Installation du framework
- Configuration du firewall

**deploy_app.sh**
- Clone du dépôt GitHub
- Installation des dépendances app
- Configuration du service systemd
- Démarrage de l'application

---

## Flux de Déploiement

### Étape 1: Requête Utilisateur
```
Utilisateur → Interface Web → POST /api/deploy
```

### Étape 2: Validation
```
Backend → Validation des données
        → Vérification du framework
        → Vérification des ressources
```

### Étape 3: Création Base de Données
```
Backend → Création entrée Deployment
        → Status: "pending"
```

### Étape 4: Provisionnement Infrastructure
```
TerraformService → Génération .tf
                 → terraform init
                 → terraform apply
                 → Création VM/LXC
```

### Étape 5: Récupération Informations
```
TerraformService → terraform output
                 → Récupération IP et VM ID
                 → Mise à jour base de données
```

### Étape 6: Installation Framework
```
DeploymentService → Génération script install
                  → Exécution via SSH
                  → Installation dépendances
```

### Étape 7: Déploiement Application
```
DeploymentService → Génération script deploy
                  → Clone GitHub
                  → Installation dépendances app
                  → Configuration service
                  → Démarrage application
```

### Étape 8: Finalisation
```
Backend → Status: "running"
        → deployed_at: timestamp
        → Notification utilisateur
```

---

## Modèle de Données

### Deployment

```python
{
    id: Integer,
    name: String,
    type: "vm" | "lxc",
    framework: String,
    github_url: String,
    cpu: Integer,
    memory: Integer,
    disk: Integer,
    proxmox_id: Integer,
    proxmox_node: String,
    ip_address: String,
    status: "pending" | "creating" | "running" | "failed" | "stopped",
    error_message: String,
    created_at: DateTime,
    updated_at: DateTime,
    deployed_at: DateTime,
    terraform_output: Text,
    deployment_log: Text
}
```

---

## Sécurité

### Authentification
- Token API Proxmox
- Séparation des privilèges

### Validation
- Validation des URLs GitHub
- Limitation des ressources
- Sanitization des inputs

### Réseau
- Firewall UFW
- Isolation des VMs
- Ports spécifiques par framework

---

## Performance

### Optimisations
- Déploiements asynchrones
- Pool de connexions DB
- Cache des ressources Proxmox
- Logs structurés

### Limitations
- Max 8 CPU par déploiement
- Max 16 GB RAM par déploiement
- Max 500 GB disque par déploiement

---

## Scalabilité

### Horizontal
- Support multi-nœuds Proxmox
- Load balancing possible
- Base de données distribuée

### Vertical
- Optimisation des ressources
- Monitoring des performances
- Auto-scaling (futur)

---

## Monitoring

### Métriques
- Nombre de déploiements
- Taux de succès
- Temps de déploiement
- Utilisation ressources Proxmox

### Logs
- Logs application (app.log)
- Logs déploiement (par ID)
- Logs Terraform
- Logs système

---

## Évolutions Futures

1. **WebSocket pour suivi en temps réel**
2. **Support Docker Swarm / Kubernetes**
3. **CI/CD intégré**
4. **Multi-tenancy**
5. **Backup automatique**
6. **Auto-scaling**
7. **Monitoring avancé (Prometheus/Grafana)**
8. **Support base de données managées**
