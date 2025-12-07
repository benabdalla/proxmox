.PHONY: help install start test clean dev deploy status logs check-config

# Variables
PYTHON := python3
PIP := pip3
VENV := backend/venv
BACKEND := backend
FRONTEND := frontend

help: ## Afficher l'aide
	@echo "Plateforme PaaS - Commandes disponibles:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""

check-config: ## Vérifier la configuration Proxmox et templates
	@echo "🔍 Vérification de la configuration..."
	@if [ -f "check-proxmox-templates.sh" ]; then \
		chmod +x check-proxmox-templates.sh; \
		./check-proxmox-templates.sh; \
	else \
		echo "❌ Script de vérification non trouvé"; \
	fi

install: ## Installer les dépendances
	@echo "📦 Installation des dépendances..."
	@mkdir -p data logs terraform/workspaces terraform/states
	@cd $(BACKEND) && $(PYTHON) -m venv venv
	@. $(VENV)/bin/activate && $(PIP) install -r $(BACKEND)/requirements.txt
	@echo "✅ Installation terminée"
	@echo ""
	@echo "⚙️  Prochaine étape: make check-config"

start: ## Démarrer l'application
	@echo "🚀 Démarrage de l'application..."
	@. $(VENV)/bin/activate && cd $(BACKEND) && $(PYTHON) app.py

dev: ## Démarrer en mode développement
	@echo "🔧 Démarrage en mode développement..."
	@. $(VENV)/bin/activate && cd $(BACKEND) && FLASK_DEBUG=True $(PYTHON) app.py

test: ## Lancer les tests
	@echo "🧪 Exécution des tests..."
	@. $(VENV)/bin/activate && pytest tests/ -v --cov=$(BACKEND) --cov-report=html
	@echo "✅ Tests terminés - Rapport: htmlcov/index.html"

test-watch: ## Lancer les tests en mode watch
	@. $(VENV)/bin/activate && pytest-watch tests/

lint: ## Vérifier le code
	@echo "🔍 Analyse du code..."
	@. $(VENV)/bin/activate && flake8 $(BACKEND) --max-line-length=120

format: ## Formater le code
	@echo "✨ Formatage du code..."
	@. $(VENV)/bin/activate && black $(BACKEND)

status: ## Afficher le statut
	@echo "📊 Statut du système:"
	@curl -s http://localhost:5000/api/status | python -m json.tool || echo "❌ Application non accessible"

deployments: ## Lister les déploiements
	@echo "📋 Liste des déploiements:"
	@curl -s http://localhost:5000/api/deployments | python -m json.tool || echo "❌ Application non accessible"

resources: ## Afficher les ressources Proxmox
	@echo "💻 Ressources Proxmox:"
	@curl -s http://localhost:5000/api/resources | python -m json.tool || echo "❌ Application non accessible"

logs: ## Afficher les logs
	@tail -f logs/app.log

clean: ## Nettoyer les fichiers temporaires
	@echo "🧹 Nettoyage..."
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@rm -rf .pytest_cache htmlcov .coverage
	@echo "✅ Nettoyage terminé"

clean-all: clean ## Nettoyer tout (y compris venv et data)
	@echo "🧹 Nettoyage complet..."
	@rm -rf $(VENV)
	@rm -rf data/*.db
	@rm -rf logs/*.log
	@rm -rf terraform/workspaces/*
	@rm -rf terraform/states/*
	@echo "✅ Nettoyage complet terminé"

backup: ## Sauvegarder la base de données
	@echo "💾 Sauvegarde de la base de données..."
	@mkdir -p backups
	@cp data/deployments.db backups/deployments-$(shell date +%Y%m%d-%H%M%S).db
	@echo "✅ Sauvegarde créée dans backups/"

restore: ## Restaurer la dernière sauvegarde
	@echo "📦 Restauration de la dernière sauvegarde..."
	@cp $(shell ls -t backups/deployments-*.db | head -1) data/deployments.db
	@echo "✅ Base de données restaurée"

deploy-example: ## Déployer un exemple Django
	@echo "🚀 Déploiement d'un exemple Django..."
	@curl -X POST http://localhost:5000/api/deploy \
		-H "Content-Type: application/json" \
		-d '{"type":"vm","framework":"django","github_url":"https://github.com/django/django.git","cpu":2,"memory":2048,"disk":20}'

docker-build: ## Construire l'image Docker (futur)
	@echo "🐳 Construction de l'image Docker..."
	@docker build -t paas-platform:latest .

docker-run: ## Lancer avec Docker (futur)
	@echo "🐳 Lancement avec Docker..."
	@docker run -p 5000:5000 --env-file .env paas-platform:latest

setup-proxmox: ## Afficher les commandes de configuration Proxmox
	@echo "⚙️  Configuration Proxmox:"
	@echo ""
	@echo "Exécutez ces commandes sur votre serveur Proxmox:"
	@echo ""
	@echo "  pveum user add terraform@pve"
	@echo "  pveum aclmod / -user terraform@pve -role PVEAdmin"
	@echo "  pveum user token add terraform@pve terraform-token --privsep=0"
	@echo ""
	@echo "Puis copiez le token dans votre fichier .env"

check-deps: ## Vérifier les dépendances système
	@echo "🔍 Vérification des dépendances..."
	@command -v $(PYTHON) >/dev/null 2>&1 || { echo "❌ Python 3 non installé"; exit 1; }
	@command -v terraform >/dev/null 2>&1 || echo "⚠️  Terraform non installé"
	@command -v git >/dev/null 2>&1 || echo "⚠️  Git non installé"
	@echo "✅ Vérification terminée"

init: check-deps install ## Initialisation complète du projet
	@echo "🎉 Projet initialisé avec succès!"
	@echo ""
	@echo "Prochaines étapes:"
	@echo "  1. Configurer .env avec vos paramètres Proxmox"
	@echo "  2. Lancer l'application: make start"
	@echo "  3. Accéder à http://localhost:5000"

.DEFAULT_GOAL := help
