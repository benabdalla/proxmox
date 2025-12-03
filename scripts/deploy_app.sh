#!/bin/bash
################################################################################
# Script de déploiement d'application
# Généré automatiquement par la plateforme PaaS
################################################################################

set -e

FRAMEWORK="$1"
GITHUB_URL="$2"
PORT="${3:-8000}"

echo "================================================"
echo "🚀 Déploiement de l'application"
echo "================================================"
echo "Framework: $FRAMEWORK"
echo "Source: $GITHUB_URL"
echo "Port: $PORT"
echo ""

# Dossier de travail
APP_DIR="/opt/app"
cd /opt
rm -rf "$APP_DIR"

# Clone du dépôt
echo "📥 Clone du dépôt GitHub..."
git clone "$GITHUB_URL" "$APP_DIR"
cd "$APP_DIR"

# Déploiement selon le framework
case $FRAMEWORK in
    django)
        echo "🐍 Configuration Django..."
        python3 -m venv venv
        source venv/bin/activate
        
        if [ -f requirements.txt ]; then
            pip install -r requirements.txt
        fi
        
        python manage.py migrate --noinput
        python manage.py collectstatic --noinput
        
        # Service systemd
        cat > /etc/systemd/system/app.service << EOF
[Unit]
Description=Django Application
After=network.target

[Service]
User=root
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
ExecStart=$APP_DIR/venv/bin/gunicorn --bind 0.0.0.0:$PORT --workers 3 wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
EOF
        ;;
        
    flask)
        echo "🐍 Configuration Flask..."
        python3 -m venv venv
        source venv/bin/activate
        
        if [ -f requirements.txt ]; then
            pip install -r requirements.txt
        fi
        
        cat > /etc/systemd/system/app.service << EOF
[Unit]
Description=Flask Application
After=network.target

[Service]
User=root
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
ExecStart=$APP_DIR/venv/bin/gunicorn --bind 0.0.0.0:$PORT --workers 3 app:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF
        ;;
        
    fastapi)
        echo "🐍 Configuration FastAPI..."
        python3 -m venv venv
        source venv/bin/activate
        
        if [ -f requirements.txt ]; then
            pip install -r requirements.txt
        fi
        
        cat > /etc/systemd/system/app.service << EOF
[Unit]
Description=FastAPI Application
After=network.target

[Service]
User=root
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
ExecStart=$APP_DIR/venv/bin/uvicorn main:app --host 0.0.0.0 --port $PORT
Restart=always

[Install]
WantedBy=multi-user.target
EOF
        ;;
        
    nodejs|express)
        echo "📗 Configuration Node.js..."
        npm install
        
        cat > /etc/systemd/system/app.service << EOF
[Unit]
Description=Node.js Application
After=network.target

[Service]
User=root
WorkingDirectory=$APP_DIR
Environment="PORT=$PORT"
ExecStart=/usr/bin/node server.js
Restart=always

[Install]
WantedBy=multi-user.target
EOF
        ;;
        
    react|vue)
        echo "⚛️ Build de l'application frontend..."
        npm install
        npm run build
        npm install -g serve
        
        cat > /etc/systemd/system/app.service << EOF
[Unit]
Description=Static Web Application
After=network.target

[Service]
User=root
WorkingDirectory=$APP_DIR
ExecStart=/usr/bin/serve -s build -l $PORT
Restart=always

[Install]
WantedBy=multi-user.target
EOF
        ;;
        
    nextjs)
        echo "▲ Configuration Next.js..."
        npm install
        npm run build
        
        cat > /etc/systemd/system/app.service << EOF
[Unit]
Description=Next.js Application
After=network.target

[Service]
User=root
WorkingDirectory=$APP_DIR
Environment="PORT=$PORT"
ExecStart=/usr/bin/npm start
Restart=always

[Install]
WantedBy=multi-user.target
EOF
        ;;
        
    laravel)
        echo "🐘 Configuration Laravel..."
        composer install --no-dev --optimize-autoloader
        
        if [ -f .env.example ]; then
            cp .env.example .env
        fi
        
        php artisan key:generate
        php artisan migrate --force
        
        chown -R www-data:www-data storage bootstrap/cache
        
        # Configuration Nginx
        cat > /etc/nginx/sites-available/app << EOF
server {
    listen $PORT;
    root $APP_DIR/public;
    index index.php;

    location / {
        try_files \$uri \$uri/ /index.php?\$query_string;
    }

    location ~ \.php$ {
        fastcgi_pass unix:/var/run/php/php8.1-fpm.sock;
        fastcgi_index index.php;
        fastcgi_param SCRIPT_FILENAME \$document_root\$fastcgi_script_name;
        include fastcgi_params;
    }
}
EOF
        
        ln -sf /etc/nginx/sites-available/app /etc/nginx/sites-enabled/
        rm -f /etc/nginx/sites-enabled/default
        systemctl restart nginx
        systemctl restart php8.1-fpm
        
        echo "✅ Laravel configuré avec Nginx"
        exit 0
        ;;
        
    springboot)
        echo "☕ Build Spring Boot..."
        mvn clean package -DskipTests
        
        cat > /etc/systemd/system/app.service << EOF
[Unit]
Description=Spring Boot Application
After=network.target

[Service]
User=root
WorkingDirectory=$APP_DIR
ExecStart=/usr/bin/java -jar target/*.jar --server.port=$PORT
Restart=always

[Install]
WantedBy=multi-user.target
EOF
        ;;
        
    *)
        echo "❌ Framework non supporté: $FRAMEWORK"
        exit 1
        ;;
esac

# Démarrer le service (sauf pour Laravel qui utilise Nginx)
if [ "$FRAMEWORK" != "laravel" ]; then
    echo "🔄 Démarrage du service..."
    systemctl daemon-reload
    systemctl enable app
    systemctl start app
    
    echo "✅ Service démarré!"
fi

echo "================================================"
echo "🎉 Déploiement terminé!"
echo "🌐 Application accessible sur le port $PORT"
echo "================================================"
