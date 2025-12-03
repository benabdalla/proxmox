@echo off
REM ################################################################################
REM Script de démarrage rapide de la plateforme PaaS (Windows)
REM ################################################################################

echo ================================================
echo 🚀 Démarrage Plateforme PaaS
echo ================================================

REM Vérifier Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python n'est pas installé
    pause
    exit /b 1
)

echo ✅ Python installé

REM Vérifier Terraform
terraform --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Terraform n'est pas installé
    echo 📥 Installation recommandée: https://www.terraform.io/downloads
)

REM Créer les dossiers nécessaires
echo 📁 Création des dossiers...
if not exist "data" mkdir data
if not exist "logs" mkdir logs
if not exist "terraform\workspaces" mkdir terraform\workspaces
if not exist "terraform\states" mkdir terraform\states

REM Vérifier le fichier .env
if not exist ".env" (
    echo ⚠️  Fichier .env non trouvé
    echo 📝 Copie de .env.example vers .env
    copy .env.example .env
    echo ⚠️  Veuillez configurer le fichier .env avec vos paramètres Proxmox
    pause
    exit /b 1
)

REM Vérifier l'environnement virtuel
if not exist "backend\venv" (
    echo 📦 Création de l'environnement virtuel Python...
    cd backend
    python -m venv venv
    call venv\Scripts\activate.bat
    
    echo 📦 Installation des dépendances...
    python -m pip install --quiet --upgrade pip
    pip install --quiet -r requirements.txt
    
    cd ..
) else (
    echo ✅ Environnement virtuel existant
)

REM Activer l'environnement virtuel
call backend\venv\Scripts\activate.bat

REM Lancer l'application
echo.
echo ================================================
echo 🎉 Lancement de l'application...
echo ================================================
echo.

cd backend
python app.py
