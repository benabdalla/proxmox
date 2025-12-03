"""
Générateur de scripts d'installation et de déploiement
"""

from utils.config import Config

def generate_install_script(framework, deployment_type='vm'):
    """
    Génère un script d'installation pour un framework
    
    Args:
        framework: Le framework à installer
        deployment_type: Type de déploiement (vm ou lxc)
        
    Returns:
        Script bash d'installation
    """
    
    framework_info = Config.get_framework_info(framework)
    if not framework_info:
        raise ValueError(f"Framework non supporté: {framework}")
    
    language = framework_info['language']
    
    # En-tête commun
    script = """#!/bin/bash
set -e

echo "🔧 Installation du framework: {framework}"
echo "================================================"

# Mise à jour du système
apt-get update
apt-get upgrade -y

# Utilitaires de base
apt-get install -y curl wget git nano vim htop net-tools

""".format(framework=framework)
    
    # Installation selon le langage
    if language == 'python':
        script += generate_python_install(framework)
    elif language == 'javascript':
        script += generate_javascript_install(framework)
    elif language == 'php':
        script += generate_php_install(framework)
    elif language == 'java':
        script += generate_java_install(framework)
    
    # Configuration firewall
    port = framework_info['port']
    script += f"""
# Configuration du firewall
apt-get install -y ufw
ufw allow {port}/tcp
ufw allow 22/tcp
ufw --force enable

echo "✅ Installation terminée!"
"""
    
    return script

def generate_python_install(framework):
    """Installation pour frameworks Python"""
    script = """
# Installation Python et pip
apt-get install -y python3 python3-pip python3-venv

# Outils Python
pip3 install --upgrade pip setuptools wheel

"""
    
    if framework == 'django':
        script += """
# Django
pip3 install django gunicorn psycopg2-binary

"""
    elif framework == 'flask':
        script += """
# Flask
pip3 install flask gunicorn

"""
    elif framework == 'fastapi':
        script += """
# FastAPI
pip3 install fastapi uvicorn[standard]

"""
    
    return script

def generate_javascript_install(framework):
    """Installation pour frameworks JavaScript"""
    script = """
# Installation Node.js (LTS)
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt-get install -y nodejs

# Mise à jour npm
npm install -g npm@latest

"""
    
    if framework in ['react', 'vue', 'nextjs']:
        script += """
# Outils de build
npm install -g yarn

"""
    
    return script

def generate_php_install(framework):
    """Installation pour frameworks PHP"""
    script = """
# Installation PHP et extensions
apt-get install -y php8.1 php8.1-cli php8.1-fpm php8.1-mysql \\
    php8.1-xml php8.1-mbstring php8.1-curl php8.1-zip php8.1-gd

# Composer
curl -sS https://getcomposer.org/installer | php
mv composer.phar /usr/local/bin/composer
chmod +x /usr/local/bin/composer

"""
    
    if framework == 'laravel':
        script += """
# Laravel
composer global require laravel/installer

"""
    
    return script

def generate_java_install(framework):
    """Installation pour frameworks Java"""
    return """
# Installation Java 17
apt-get install -y openjdk-17-jdk maven

# Variables d'environnement
echo 'export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64' >> /etc/profile
echo 'export PATH=$PATH:$JAVA_HOME/bin' >> /etc/profile

"""

def generate_deploy_script(framework, github_url, deployment_type='vm'):
    """
    Génère un script de déploiement pour une application
    
    Args:
        framework: Le framework de l'application
        github_url: URL du dépôt GitHub
        deployment_type: Type de déploiement (vm ou lxc)
        
    Returns:
        Script bash de déploiement
    """
    
    framework_info = Config.get_framework_info(framework)
    if not framework_info:
        raise ValueError(f"Framework non supporté: {framework}")
    
    language = framework_info['language']
    port = framework_info['port']
    
    # En-tête
    script = f"""#!/bin/bash
set -e

echo "🚀 Déploiement de l'application"
echo "================================================"
echo "Framework: {framework}"
echo "Source: {github_url}"
echo "Port: {port}"
echo ""

# Dossier de travail
cd /opt
rm -rf app

# Clone du dépôt
echo "📥 Clone du dépôt..."
git clone {github_url} app
cd app

"""
    
    # Déploiement selon le langage
    if language == 'python':
        script += generate_python_deploy(framework, port)
    elif language == 'javascript':
        script += generate_javascript_deploy(framework, port)
    elif language == 'php':
        script += generate_php_deploy(framework, port)
    elif language == 'java':
        script += generate_java_deploy(framework, port)
    
    script += """
echo "✅ Déploiement terminé!"
echo "🌐 Application accessible sur le port {port}"
""".format(port=port)
    
    return script

def generate_python_deploy(framework, port):
    """Déploiement pour frameworks Python"""
    script = """
# Environnement virtuel
python3 -m venv venv
source venv/bin/activate

# Installation des dépendances
if [ -f requirements.txt ]; then
    pip install -r requirements.txt
fi

"""
    
    if framework == 'django':
        script += f"""
# Django
python manage.py migrate
python manage.py collectstatic --noinput

# Gunicorn service
cat > /etc/systemd/system/app.service << EOF
[Unit]
Description=Django Application
After=network.target

[Service]
User=root
WorkingDirectory=/opt/app
Environment="PATH=/opt/app/venv/bin"
ExecStart=/opt/app/venv/bin/gunicorn --bind 0.0.0.0:{port} --workers 3 wsgi:application

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable app
systemctl start app
"""
    
    elif framework == 'flask':
        script += f"""
# Flask
cat > /etc/systemd/system/app.service << EOF
[Unit]
Description=Flask Application
After=network.target

[Service]
User=root
WorkingDirectory=/opt/app
Environment="PATH=/opt/app/venv/bin"
ExecStart=/opt/app/venv/bin/gunicorn --bind 0.0.0.0:{port} --workers 3 app:app

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable app
systemctl start app
"""
    
    elif framework == 'fastapi':
        script += f"""
# FastAPI
cat > /etc/systemd/system/app.service << EOF
[Unit]
Description=FastAPI Application
After=network.target

[Service]
User=root
WorkingDirectory=/opt/app
Environment="PATH=/opt/app/venv/bin"
ExecStart=/opt/app/venv/bin/uvicorn main:app --host 0.0.0.0 --port {port}

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable app
systemctl start app
"""
    
    return script

def generate_javascript_deploy(framework, port):
    """Déploiement pour frameworks JavaScript"""
    script = """
# Installation des dépendances
npm install

"""
    
    if framework in ['react', 'vue']:
        script += f"""
# Build de production
npm run build

# Serveur statique
npm install -g serve
cat > /etc/systemd/system/app.service << EOF
[Unit]
Description=Static Web Application
After=network.target

[Service]
User=root
WorkingDirectory=/opt/app
ExecStart=/usr/bin/serve -s build -l {port}

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable app
systemctl start app
"""
    
    elif framework == 'nextjs':
        script += f"""
# Build Next.js
npm run build

# Service Next.js
cat > /etc/systemd/system/app.service << EOF
[Unit]
Description=Next.js Application
After=network.target

[Service]
User=root
WorkingDirectory=/opt/app
Environment="PORT={port}"
ExecStart=/usr/bin/npm start

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable app
systemctl start app
"""
    
    else:  # nodejs/express
        script += f"""
# Service Node.js
cat > /etc/systemd/system/app.service << EOF
[Unit]
Description=Node.js Application
After=network.target

[Service]
User=root
WorkingDirectory=/opt/app
Environment="PORT={port}"
ExecStart=/usr/bin/node server.js

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable app
systemctl start app
"""
    
    return script

def generate_php_deploy(framework, port):
    """Déploiement pour frameworks PHP"""
    if framework == 'laravel':
        return f"""
# Installation des dépendances
composer install --no-dev --optimize-autoloader

# Configuration
cp .env.example .env
php artisan key:generate
php artisan migrate --force

# Permissions
chown -R www-data:www-data storage bootstrap/cache

# PHP-FPM et Nginx
apt-get install -y nginx

cat > /etc/nginx/sites-available/app << EOF
server {{
    listen {port};
    root /opt/app/public;
    index index.php;

    location / {{
        try_files \$uri \$uri/ /index.php?\$query_string;
    }}

    location ~ \\.php$ {{
        fastcgi_pass unix:/var/run/php/php8.1-fpm.sock;
        fastcgi_index index.php;
        fastcgi_param SCRIPT_FILENAME \$document_root\$fastcgi_script_name;
        include fastcgi_params;
    }}
}}
EOF

ln -sf /etc/nginx/sites-available/app /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
systemctl restart nginx
systemctl restart php8.1-fpm
"""
    
    return ""

def generate_java_deploy(framework, port):
    """Déploiement pour frameworks Java"""
    if framework == 'springboot':
        return f"""
# Build Maven
mvn clean package -DskipTests

# Service Spring Boot
cat > /etc/systemd/system/app.service << EOF
[Unit]
Description=Spring Boot Application
After=network.target

[Service]
User=root
WorkingDirectory=/opt/app
ExecStart=/usr/bin/java -jar target/*.jar --server.port={port}

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable app
systemctl start app
"""
    
    return ""
