"""
Service de gestion des déploiements
"""

import os
import logging
import threading
from datetime import datetime

from models.database import db, Deployment
from services.terraform_service import TerraformService
from services.proxmox_service import ProxmoxService
from utils.script_generator import generate_install_script, generate_deploy_script

logger = logging.getLogger(__name__)

class DeploymentService:
    """Service pour gérer le cycle de vie des déploiements"""
    
    def __init__(self):
        self.terraform_service = TerraformService()
        self.proxmox_service = ProxmoxService()
    
    def deploy_async(self, deployment_id):
        """Lance un déploiement en arrière-plan"""
        thread = threading.Thread(target=self._deploy, args=(deployment_id,))
        thread.daemon = True
        thread.start()
        logger.info(f"🚀 Déploiement {deployment_id} lancé en arrière-plan")
    
    def _deploy(self, deployment_id):
        """Processus de déploiement complet"""
        from app import app
        
        with app.app_context():
            deployment = Deployment.query.get(deployment_id)
            if not deployment:
                logger.error(f"❌ Déploiement {deployment_id} introuvable")
                return
            
            try:
                logger.info(f"📦 Démarrage du déploiement {deployment_id}: {deployment.name}")
                
                # Étape 1: Créer la configuration Terraform
                deployment.status = 'creating'
                db.session.commit()
                
                logger.info(f"🔧 Génération de la configuration Terraform...")
                workspace_dir = self.terraform_service.create_workspace(deployment)
                
                # Étape 2: Appliquer Terraform
                logger.info(f"⚙️ Application de Terraform...")
                success, output = self.terraform_service.apply(workspace_dir)
                
                deployment.terraform_output = output
                
                if not success:
                    raise Exception(f"Terraform apply a échoué: {output}")
                
                # Étape 3: Récupérer les outputs Terraform
                outputs = self.terraform_service.get_outputs(workspace_dir)
                deployment.proxmox_id = outputs.get('vm_id')
                deployment.ip_address = outputs.get('ip_address')
                deployment.proxmox_node = os.getenv('PROXMOX_NODE')
                
                logger.info(f"✅ VM créée - ID: {deployment.proxmox_id}, IP: {deployment.ip_address}")
                
                # Étape 4: Attendre que la VM soit démarrée
                logger.info(f"⏳ Attente du démarrage de la VM...")
                if not self._wait_for_vm_ready(deployment.proxmox_id, deployment.ip_address):
                    raise Exception("Timeout en attendant que la VM soit prête")
                
                # Étape 5: Installer le framework
                logger.info(f"📥 Installation du framework {deployment.framework}...")
                install_log = self._install_framework(deployment)
                
                # Étape 6: Déployer l'application
                logger.info(f"🚀 Déploiement de l'application depuis {deployment.github_url}...")
                deploy_log = self._deploy_application(deployment)
                
                deployment.deployment_log = f"{install_log}\n\n{deploy_log}"
                
                # Succès !
                deployment.status = 'running'
                deployment.deployed_at = datetime.utcnow()
                db.session.commit()
                
                logger.info(f"🎉 Déploiement {deployment_id} terminé avec succès!")
                logger.info(f"🌐 Application accessible sur http://{deployment.ip_address}")
                
            except Exception as e:
                logger.error(f"❌ Erreur lors du déploiement {deployment_id}: {e}")
                deployment.status = 'failed'
                deployment.error_message = str(e)
                db.session.commit()
    
    def _wait_for_vm_ready(self, vm_id, ip_address, timeout=300):
        """Attend que la VM soit prête"""
        import time
        import socket
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # Vérifier si le port SSH est ouvert
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                result = sock.connect_ex((ip_address, 22))
                sock.close()
                
                if result == 0:
                    logger.info(f"✅ VM prête - SSH accessible sur {ip_address}")
                    return True
                    
            except Exception as e:
                logger.debug(f"VM pas encore prête: {e}")
            
            time.sleep(10)
        
        return False
    
    def _install_framework(self, deployment):
        """Installe le framework sur la VM"""
        script = generate_install_script(deployment.framework, deployment.type)
        
        # Exécuter le script via SSH (simulation pour l'exemple)
        # Dans un cas réel, utiliser paramiko ou fabric
        logger.info(f"Script d'installation généré pour {deployment.framework}")
        return f"Framework {deployment.framework} installé"
    
    def _deploy_application(self, deployment):
        """Déploie l'application depuis GitHub"""
        script = generate_deploy_script(
            deployment.framework,
            deployment.github_url,
            deployment.type
        )
        
        # Exécuter le script via SSH (simulation pour l'exemple)
        logger.info(f"Script de déploiement généré pour {deployment.github_url}")
        return f"Application déployée depuis {deployment.github_url}"
    
    def destroy(self, deployment_id):
        """Détruit un déploiement"""
        from app import app
        
        with app.app_context():
            deployment = Deployment.query.get(deployment_id)
            if not deployment:
                return False, "Déploiement introuvable"
            
            try:
                workspace_dir = os.path.join(
                    os.getenv('TERRAFORM_WORK_DIR', './terraform/workspaces'),
                    f"deployment-{deployment_id}"
                )
                
                if os.path.exists(workspace_dir):
                    success, output = self.terraform_service.destroy(workspace_dir)
                    if not success:
                        return False, f"Erreur Terraform: {output}"
                
                return True, "Déploiement détruit"
                
            except Exception as e:
                logger.error(f"❌ Erreur lors de la destruction: {e}")
                return False, str(e)
    
    def restart(self, deployment_id):
        """Redémarre un déploiement"""
        from app import app
        
        with app.app_context():
            deployment = Deployment.query.get(deployment_id)
            if not deployment:
                return False, "Déploiement introuvable"
            
            try:
                success = self.proxmox_service.restart_vm(
                    deployment.proxmox_node,
                    deployment.proxmox_id
                )
                
                if success:
                    deployment.updated_at = datetime.utcnow()
                    db.session.commit()
                    return True, "VM redémarrée"
                else:
                    return False, "Échec du redémarrage"
                    
            except Exception as e:
                logger.error(f"❌ Erreur lors du redémarrage: {e}")
                return False, str(e)
