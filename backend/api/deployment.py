"""
API Routes pour les déploiements
"""

import logging
from flask import Blueprint, request, jsonify
from datetime import datetime

from models.database import db, Deployment
from services.deployment_service import DeploymentService
from utils.validators import validate_deployment_request

logger = logging.getLogger(__name__)

deployment_bp = Blueprint('deployment', __name__)
deployment_service = DeploymentService()

@deployment_bp.route('/deploy', methods=['POST'])
def create_deployment():
    """
    Crée un nouveau déploiement
    
    Body JSON:
    {
        "type": "vm|lxc",
        "framework": "django|laravel|nodejs|...",
        "github_url": "https://github.com/user/repo.git",
        "cpu": 2,
        "memory": 2048,
        "disk": 20,
        "name": "optional-name"
    }
    """
    try:
        data = request.get_json()
        
        # Validation
        is_valid, error_message = validate_deployment_request(data)
        if not is_valid:
            return jsonify({'error': error_message}), 400
        
        # Créer l'entrée de déploiement
        deployment = Deployment(
            name=data.get('name', f"{data['framework']}-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"),
            type=data['type'],
            framework=data['framework'],
            github_url=data['github_url'],
            cpu=data.get('cpu', 2),
            memory=data.get('memory', 2048),
            disk=data.get('disk', 20),
            status='pending'
        )
        
        db.session.add(deployment)
        db.session.commit()
        
        logger.info(f"✅ Déploiement créé: {deployment.id} - {deployment.name}")
        
        # Lancer le déploiement en arrière-plan
        deployment_service.deploy_async(deployment.id)
        
        return jsonify({
            'message': 'Déploiement démarré',
            'deployment': deployment.to_dict()
        }), 202
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de la création du déploiement: {e}")
        return jsonify({'error': str(e)}), 500

@deployment_bp.route('/deployments', methods=['GET'])
def list_deployments():
    """Liste tous les déploiements"""
    try:
        deployments = Deployment.query.order_by(Deployment.created_at.desc()).all()
        return jsonify({
            'deployments': [d.to_dict() for d in deployments],
            'total': len(deployments)
        })
    except Exception as e:
        logger.error(f"❌ Erreur lors de la récupération des déploiements: {e}")
        return jsonify({'error': str(e)}), 500

@deployment_bp.route('/deployments/<int:deployment_id>', methods=['GET'])
def get_deployment(deployment_id):
    """Récupère les détails d'un déploiement"""
    try:
        deployment = Deployment.query.get(deployment_id)
        if not deployment:
            return jsonify({'error': 'Déploiement introuvable'}), 404
        
        return jsonify(deployment.to_dict())
    except Exception as e:
        logger.error(f"❌ Erreur lors de la récupération du déploiement {deployment_id}: {e}")
        return jsonify({'error': str(e)}), 500

@deployment_bp.route('/deployments/<int:deployment_id>', methods=['DELETE'])
def delete_deployment(deployment_id):
    """Supprime un déploiement"""
    try:
        deployment = Deployment.query.get(deployment_id)
        if not deployment:
            return jsonify({'error': 'Déploiement introuvable'}), 404
        
        # Détruire l'infrastructure
        success, message = deployment_service.destroy(deployment_id)
        
        if success:
            deployment.status = 'deleted'
            deployment.updated_at = datetime.utcnow()
            db.session.commit()
            
            return jsonify({
                'message': 'Déploiement supprimé',
                'deployment_id': deployment_id
            })
        else:
            return jsonify({'error': message}), 500
            
    except Exception as e:
        logger.error(f"❌ Erreur lors de la suppression du déploiement {deployment_id}: {e}")
        return jsonify({'error': str(e)}), 500

@deployment_bp.route('/deployments/<int:deployment_id>/logs', methods=['GET'])
def get_deployment_logs(deployment_id):
    """Récupère les logs d'un déploiement"""
    try:
        deployment = Deployment.query.get(deployment_id)
        if not deployment:
            return jsonify({'error': 'Déploiement introuvable'}), 404
        
        return jsonify({
            'deployment_id': deployment_id,
            'terraform_output': deployment.terraform_output,
            'deployment_log': deployment.deployment_log
        })
    except Exception as e:
        logger.error(f"❌ Erreur lors de la récupération des logs {deployment_id}: {e}")
        return jsonify({'error': str(e)}), 500

@deployment_bp.route('/deployments/<int:deployment_id>/restart', methods=['POST'])
def restart_deployment(deployment_id):
    """Redémarre un déploiement"""
    try:
        deployment = Deployment.query.get(deployment_id)
        if not deployment:
            return jsonify({'error': 'Déploiement introuvable'}), 404
        
        success, message = deployment_service.restart(deployment_id)
        
        if success:
            return jsonify({
                'message': 'Déploiement redémarré',
                'deployment_id': deployment_id
            })
        else:
            return jsonify({'error': message}), 500
            
    except Exception as e:
        logger.error(f"❌ Erreur lors du redémarrage du déploiement {deployment_id}: {e}")
        return jsonify({'error': str(e)}), 500
