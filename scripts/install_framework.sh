#!/bin/bash
################################################################################
# Script d'installation du framework
# Généré automatiquement par la plateforme PaaS
################################################################################

set -e

FRAMEWORK="$1"
DEPLOYMENT_TYPE="${2:-vm}"

echo "================================================"
echo "🔧 Installation du framework: $FRAMEWORK"
echo "================================================"

# Mise à jour du système
echo "📦 Mise à jour du système..."
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get upgrade -y -qq

# Utilitaires de base
echo "📦 Installation des utilitaires..."
apt-get install -y -qq curl wget git nano vim htop net-tools ufw

# Installation selon le framework
case $FRAMEWORK in
    django|flask|fastapi)
        echo "🐍 Installation Python..."
        apt-get install -y -qq python3 python3-pip python3-venv
        pip3 install --quiet --upgrade pip setuptools wheel
        
        if [ "$FRAMEWORK" = "django" ]; then
            pip3 install --quiet django gunicorn psycopg2-binary
        elif [ "$FRAMEWORK" = "flask" ]; then
            pip3 install --quiet flask gunicorn
        elif [ "$FRAMEWORK" = "fastapi" ]; then
            pip3 install --quiet fastapi uvicorn[standard]
        fi
        ;;
        
    nodejs|express|react|vue|nextjs)
        echo "📗 Installation Node.js..."
        curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
        apt-get install -y -qq nodejs
        npm install -g npm@latest --silent
        
        if [[ "$FRAMEWORK" =~ ^(react|vue|nextjs)$ ]]; then
            npm install -g yarn --silent
        fi
        ;;
        
    laravel|symfony)
        echo "🐘 Installation PHP..."
        apt-get install -y -qq php8.1 php8.1-cli php8.1-fpm php8.1-mysql \
            php8.1-xml php8.1-mbstring php8.1-curl php8.1-zip php8.1-gd
        
        curl -sS https://getcomposer.org/installer | php
        mv composer.phar /usr/local/bin/composer
        chmod +x /usr/local/bin/composer
        
        if [ "$FRAMEWORK" = "laravel" ]; then
            apt-get install -y -qq nginx
        fi
        ;;
        
    springboot)
        echo "☕ Installation Java..."
        apt-get install -y -qq openjdk-17-jdk maven
        echo 'export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64' >> /etc/profile
        echo 'export PATH=$PATH:$JAVA_HOME/bin' >> /etc/profile
        ;;
        
    *)
        echo "❌ Framework non supporté: $FRAMEWORK"
        exit 1
        ;;
esac

# Configuration firewall
echo "🔒 Configuration du firewall..."
ufw --force enable
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 3000/tcp
ufw allow 5000/tcp
ufw allow 8000/tcp
ufw allow 8080/tcp

echo "✅ Installation du framework terminée!"
echo "================================================"
