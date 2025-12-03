"""
Application principale Flask pour la plateforme PaaS
"""

import os
import logging
from flask import Flask, render_template, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from colorlog import ColoredFormatter

from models.database import init_db
from api.deployment import deployment_bp
from api.status import status_bp
from utils.config import Config

# Charger les variables d'environnement
load_dotenv()

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
    
    logger = logging.getLogger()
    logger.addHandler(handler)
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
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.getenv('DATABASE_PATH', './data/deployments.db')}"
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
    # Créer les dossiers nécessaires
    os.makedirs('data', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    os.makedirs('terraform/workspaces', exist_ok=True)
    os.makedirs('terraform/states', exist_ok=True)
    
    logger.info("🚀 Démarrage de la plateforme PaaS...")
    logger.info(f"📡 Interface disponible sur http://{os.getenv('FLASK_HOST', '0.0.0.0')}:{os.getenv('FLASK_PORT', 5000)}")
    
    # Lancer l'application
    app.run(
        host=os.getenv('FLASK_HOST', '0.0.0.0'),
        port=int(os.getenv('FLASK_PORT', 5000)),
        debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    )
