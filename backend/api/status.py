"""
API Routes pour le statut et les informations système
"""

import logging
from flask import Blueprint, jsonify
from services.proxmox_service import ProxmoxService
from models.database import Deployment, db

logger = logging.getLogger(__name__)

status_bp = Blueprint('status', __name__)
proxmox_service = ProxmoxService()

@status_bp.route('/status', methods=['GET'])
def get_system_status():
    """Récupère le statut général du système"""
    try:
        # Statistiques des déploiements
        total_deployments = Deployment.query.count()
        running_deployments = Deployment.query.filter_by(status='running').count()
        failed_deployments = Deployment.query.filter_by(status='failed').count()
        pending_deployments = Deployment.query.filter_by(status='pending').count()
        
        # Connexion Proxmox
        proxmox_connected = proxmox_service.test_connection()
        
        return jsonify({
            'system': {
                'status': 'operational',
                'proxmox_connected': proxmox_connected
            },
            'deployments': {
                'total': total_deployments,
                'running': running_deployments,
                'failed': failed_deployments,
                'pending': pending_deployments
            }
        })
    except Exception as e:
        logger.error(f"❌ Erreur lors de la récupération du statut: {e}")
        return jsonify({'error': str(e)}), 500

@status_bp.route('/frameworks', methods=['GET'])
def list_frameworks():
    """Liste les frameworks supportés"""
    frameworks = {
        'python': [
            {'id': 'django', 'name': 'Django', 'version': '4.x'},
            {'id': 'flask', 'name': 'Flask', 'version': '3.x'},
            {'id': 'fastapi', 'name': 'FastAPI', 'version': 'latest'}
        ],
        'javascript': [
            {'id': 'nodejs', 'name': 'Node.js/Express', 'version': '20.x'},
            {'id': 'react', 'name': 'React', 'version': '18.x'},
            {'id': 'vue', 'name': 'Vue.js', 'version': '3.x'},
            {'id': 'nextjs', 'name': 'Next.js', 'version': '14.x'}
        ],
        'php': [
            {'id': 'laravel', 'name': 'Laravel', 'version': '10.x'},
            {'id': 'symfony', 'name': 'Symfony', 'version': '6.x'}
        ],
        'java': [
            {'id': 'springboot', 'name': 'Spring Boot', 'version': '3.x'}
        ]
    }
    
    return jsonify(frameworks)

@status_bp.route('/resources', methods=['GET'])
def get_available_resources():
    """Récupère les ressources disponibles sur Proxmox"""
    try:
        resources = proxmox_service.get_cluster_resources()
        return jsonify(resources)
    except Exception as e:
        logger.error(f"❌ Erreur lors de la récupération des ressources: {e}")
        return jsonify({'error': str(e)}), 500
