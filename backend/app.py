"""
Application principale Flask pour la plateforme PaaS
"""

import os
import sys
import logging
from flask import Flask, render_template, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from colorlog import ColoredFormatter

# Forcer l'encodage UTF-8 pour éviter les erreurs avec les caractères spéciaux
if sys.platform == 'win32':
    import codecs
    # Vérifier si stdout/stderr ont déjà été wrappés
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    if hasattr(sys.stderr, 'buffer'):
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

from models.database import init_db
from api.deployment import deployment_bp
from api.status import status_bp
from utils.config import Config

# Charger les variables d'environnement depuis le fichier .env à la racine du projet
backend_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(backend_dir)
env_path = os.path.join(project_root, '.env')
load_dotenv(dotenv_path=env_path)

# Configuration du logging
def setup_logging():
    """Configure le système de logging avec couleurs"""
    formatter = ColoredFormatter(
        "%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(message)s",
        datefmt=None,
        reset=True,
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    
    # Ajouter un handler de fichier avec encodage UTF-8
    # Convertir le chemin du log en chemin absolu
    log_file = os.getenv('LOG_FILE', './logs/app.log')
    if not os.path.isabs(log_file):
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(backend_dir)
        log_file = os.path.join(project_root, log_file.lstrip('./').lstrip('.\\'))
    
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    
    logger = logging.getLogger()
    logger.addHandler(handler)
    logger.addHandler(file_handler)
    logger.setLevel(getattr(logging, os.getenv('LOG_LEVEL', 'INFO')))
    
    return logger

logger = setup_logging()

# Créer l'application Flask
def create_app():
    """Factory pour créer l'application Flask"""
    app = Flask(__name__, 
                static_folder='../frontend',
                template_folder='../frontend')
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')
    
    # Convertir le chemin de la base de données en chemin absolu
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(backend_dir)
    db_path = os.getenv('DATABASE_PATH', './data/deployments.db')
    
    # Si le chemin est relatif, le convertir en absolu depuis la racine du projet
    if not os.path.isabs(db_path):
        db_path = os.path.join(project_root, db_path.lstrip('./').lstrip('.\\'))
    
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # CORS
    CORS(app)
    
    # Initialiser la base de données
    init_db(app)
    
    # Enregistrer les blueprints
    app.register_blueprint(deployment_bp, url_prefix='/api')
    app.register_blueprint(status_bp, url_prefix='/api')
    
    # Route principale
    @app.route('/')
    def index():
        """Page d'accueil"""
        return render_template('index.html')
    
    # Routes pour les fichiers statiques
    @app.route('/css/<path:filename>')
    def serve_css(filename):
        """Servir les fichiers CSS"""
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        css_dir = os.path.join(os.path.dirname(backend_dir), 'frontend', 'css')
        return send_from_directory(css_dir, filename)
    
    @app.route('/js/<path:filename>')
    def serve_js(filename):
        """Servir les fichiers JavaScript"""
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        js_dir = os.path.join(os.path.dirname(backend_dir), 'frontend', 'js')
        return send_from_directory(js_dir, filename)
    
    # Route de santé
    @app.route('/health')
    def health():
        """Endpoint de vérification de santé"""
        return jsonify({
            'status': 'healthy',
            'service': 'PaaS Platform',
            'version': '1.0.0'
        })
    
    # Gestionnaire d'erreurs
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal error: {error}")
        return jsonify({'error': 'Internal server error'}), 500
    
    return app

# Créer l'application
app = create_app()

if __name__ == '__main__':
    # Créer les dossiers nécessaires avec chemins absolus
    import os
    
    # Obtenir le répertoire racine du projet (parent de backend/)
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(backend_dir)
    
    # Créer tous les dossiers nécessaires
    data_dir = os.path.join(project_root, 'data')
    logs_dir = os.path.join(project_root, 'logs')
    terraform_workspaces = os.path.join(project_root, 'terraform', 'workspaces')
    terraform_states = os.path.join(project_root, 'terraform', 'states')
    
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(logs_dir, exist_ok=True)
    os.makedirs(terraform_workspaces, exist_ok=True)
    os.makedirs(terraform_states, exist_ok=True)
    
    logger.info("🚀 Démarrage de la plateforme PaaS...")
    logger.info(f"📁 Répertoire de travail: {project_root}")
    logger.info(f"📡 Interface disponible sur http://{os.getenv('FLASK_HOST', '0.0.0.0')}:{os.getenv('FLASK_PORT', 5000)}")
    
    # Lancer l'application
    app.run(
        host=os.getenv('FLASK_HOST', '0.0.0.0'),
        port=int(os.getenv('FLASK_PORT', 5000)),
        debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    )
