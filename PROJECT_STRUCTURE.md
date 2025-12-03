# 📦 Structure du Projet - Plateforme PaaS

```
platforme/
│
├── 📄 README.md                      # Documentation principale
├── 📄 QUICKSTART.md                  # Guide de démarrage rapide
├── 📄 LICENSE                        # Licence MIT
├── 📄 .gitignore                     # Fichiers à ignorer par Git
├── 📄 .env.example                   # Exemple de configuration
├── 🚀 start.sh                       # Script de démarrage (Linux/Mac)
├── 🚀 start.bat                      # Script de démarrage (Windows)
│
├── 📁 backend/                       # Backend Flask (API)
│   ├── 📄 app.py                    # Application principale Flask
│   ├── 📄 requirements.txt          # Dépendances Python
│   │
│   ├── 📁 models/                   # Modèles de données
│   │   ├── __init__.py
│   │   └── database.py             # Modèle Deployment + SQLAlchemy
│   │
│   ├── 📁 api/                      # Routes API REST
│   │   ├── __init__.py
│   │   ├── deployment.py           # Endpoints déploiement
│   │   └── status.py               # Endpoints statut/info
│   │
│   ├── 📁 services/                 # Logique métier
│   │   ├── __init__.py
│   │   ├── deployment_service.py   # Orchestration déploiements
│   │   ├── terraform_service.py    # Gestion Terraform
│   │   └── proxmox_service.py      # Client API Proxmox
│   │
│   └── 📁 utils/                    # Utilitaires
│       ├── __init__.py
│       ├── config.py               # Configuration globale
│       ├── validators.py           # Validation des données
│       └── script_generator.py     # Génération scripts bash
│
├── 📁 frontend/                     # Interface web
│   ├── 📄 index.html               # Page principale
│   ├── 📁 css/
│   │   └── style.css               # Styles CSS
│   └── 📁 js/
│       └── app.js                  # Logique JavaScript
│
├── 📁 terraform/                    # Configuration Terraform
│   ├── 📁 workspaces/              # Workspaces par déploiement
│   │   └── deployment-{id}/
│   │       ├── main.tf
│   │       ├── variables.tf
│   │       └── terraform.tfvars
│   └── 📁 states/                  # États Terraform
│
├── 📁 scripts/                      # Scripts d'installation
│   ├── install_framework.sh        # Installation frameworks
│   └── deploy_app.sh               # Déploiement applications
│
├── 📁 docs/                         # Documentation complète
│   ├── 📄 INSTALLATION.md          # Guide d'installation
│   ├── 📄 DEPLOYMENT_GUIDE.md      # Guide de déploiement
│   ├── 📄 API.md                   # Documentation API
│   ├── 📄 ARCHITECTURE.md          # Architecture système
│   └── 📄 TROUBLESHOOTING.md       # Dépannage
│
├── 📁 tests/                        # Tests unitaires et d'intégration
│   ├── __init__.py
│   ├── conftest.py                 # Configuration pytest
│   ├── README.md                   # Guide des tests
│   └── test_validators.py         # Tests de validation
│
├── 📁 data/                         # Données de l'application (généré)
│   └── deployments.db              # Base de données SQLite
│
└── 📁 logs/                         # Logs de l'application (généré)
    ├── app.log                     # Logs généraux
    └── deployment-{id}.log         # Logs par déploiement
```

## 📊 Statistiques du Projet

- **Langage principal :** Python 🐍
- **Framework web :** Flask
- **Base de données :** SQLite
- **Infrastructure :** Terraform + Proxmox
- **Frontend :** HTML5 + CSS3 + JavaScript
- **Total de fichiers :** ~40+
- **Lignes de code :** ~3000+

## 🎯 Fonctionnalités Principales

### ✅ Backend (Python/Flask)
- API REST complète
- Gestion asynchrone des déploiements
- Intégration Terraform et Proxmox
- Base de données SQLite
- Logging détaillé
- Validation des données

### ✅ Frontend (Web)
- Interface utilisateur moderne
- Formulaire de déploiement interactif
- Dashboard des déploiements
- Visualisation des ressources
- Design responsive

### ✅ Infrastructure (Terraform)
- Génération dynamique de configuration
- Support VM et LXC
- Gestion d'état automatique
- Outputs structurés

### ✅ Scripts d'automatisation
- Installation de frameworks
- Déploiement d'applications
- Configuration système
- Services systemd

### ✅ Documentation
- Guides complets
- Documentation API
- Exemples de déploiement
- Guide de dépannage

## 🔧 Technologies Utilisées

### Backend
- **Flask** - Framework web Python
- **SQLAlchemy** - ORM Python
- **Proxmoxer** - Client API Proxmox
- **python-terraform** - Wrapper Terraform
- **python-dotenv** - Variables d'environnement

### Frontend
- **HTML5** - Structure
- **CSS3** - Styles avec variables CSS
- **JavaScript ES6** - Logique client
- **Font Awesome** - Icônes

### Infrastructure
- **Terraform** - Infrastructure as Code
- **Proxmox VE** - Virtualisation
- **Bash** - Scripts système

### DevOps
- **Git** - Contrôle de version
- **pytest** - Tests unitaires
- **systemd** - Gestion de services

## 📈 Frameworks Supportés

| Catégorie | Frameworks |
|-----------|-----------|
| Python | Django, Flask, FastAPI |
| JavaScript | Node.js, Express, React, Vue.js, Next.js |
| PHP | Laravel, Symfony |
| Java | Spring Boot |

## 🚀 Démarrage Rapide

```bash
# 1. Configuration
cp .env.example .env
nano .env

# 2. Démarrage
./start.sh   # Linux/Mac
start.bat    # Windows

# 3. Accès
http://localhost:5000
```

## 📝 Contribution

1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir [LICENSE](LICENSE) pour plus de détails.

## 👥 Auteurs

- **Votre Équipe** - Développement initial

## 🙏 Remerciements

- Proxmox pour l'hyperviseur open-source
- HashiCorp pour Terraform
- La communauté Flask
- Tous les contributeurs

---

**Note :** Ce projet est une plateforme PaaS privée complète permettant le déploiement automatique d'applications web sur infrastructure Proxmox via Terraform.
