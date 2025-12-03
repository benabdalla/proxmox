#!/bin/bash

################################################################################
# Script de démarrage rapide de la plateforme PaaS
################################################################################

set -e

echo "================================================"
echo "🚀 Démarrage Plateforme PaaS"
echo "================================================"

# Vérifier Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé"
    exit 1
fi

echo "✅ Python $(python3 --version)"

# Vérifier Terraform
if ! command -v terraform &> /dev/null; then
    echo "⚠️  Terraform n'est pas installé"
    echo "📥 Installation recommandée: https://www.terraform.io/downloads"
fi

# Créer les dossiers nécessaires
echo "📁 Création des dossiers..."
mkdir -p data logs terraform/workspaces terraform/states

# Vérifier le fichier .env
if [ ! -f .env ]; then
    echo "⚠️  Fichier .env non trouvé"
    echo "📝 Copie de .env.example vers .env"
    cp .env.example .env
    echo "⚠️  Veuillez configurer le fichier .env avec vos paramètres Proxmox"
    exit 1
fi

# Vérifier les dépendances Python
if [ ! -d "backend/venv" ]; then
    echo "📦 Création de l'environnement virtuel Python..."
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    
    echo "📦 Installation des dépendances..."
    pip install -q --upgrade pip
    pip install -q -r requirements.txt
    
    cd ..
else
    echo "✅ Environnement virtuel existant"
fi

# Activer l'environnement virtuel
source backend/venv/bin/activate

# Lancer l'application
echo ""
echo "================================================"
echo "🎉 Lancement de l'application..."
echo "================================================"
echo ""

cd backend
python app.py
