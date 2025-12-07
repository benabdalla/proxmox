"""
Service Proxmox pour interagir avec l'API
"""

import os
import logging
from proxmoxer import ProxmoxAPI

logger = logging.getLogger(__name__)

class ProxmoxService:
    """Service pour interagir avec Proxmox"""
    
    def __init__(self):
        self.api_url = os.getenv('PROXMOX_API_URL', '')
        self.token_id = os.getenv('PROXMOX_API_TOKEN_ID')
        self.token_secret = os.getenv('PROXMOX_API_TOKEN_SECRET')
        self.node = os.getenv('PROXMOX_NODE', 'pve')
        self.proxmox = None
        
        self._connect()
    
    def _connect(self):
        """Se connecte à l'API Proxmox"""
        try:
            if not self.api_url or not self.token_id or not self.token_secret:
                logger.warning("⚠️ Configuration Proxmox incomplète")
                return
            
            # Parse token
            user, token_name = self.token_id.split('!')
            
            self.proxmox = ProxmoxAPI(
                self.api_url,
                user=user,
                token_name=token_name,
                token_value=self.token_secret,
                verify_ssl=False
            )
            
            logger.info(f"✅ Connecté à Proxmox: {self.api_url}")
            
        except Exception as e:
            logger.error(f"❌ Erreur de connexion à Proxmox: {e}")
            self.proxmox = None
    
    def test_connection(self):
        """Teste la connexion à Proxmox"""
        try:
            if not self.proxmox:
                return False
            
            version = self.proxmox.version.get()
            logger.info(f"✅ Proxmox version: {version.get('version')}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur test connexion: {e}")
            return False
    
    def get_cluster_resources(self):
        """Récupère les ressources du cluster"""
        try:
            if not self.proxmox:
                return {'error': 'Non connecté à Proxmox'}
            
            # Informations sur le noeud
            node_status = self.proxmox.nodes(self.node).status.get()
            
            # VMs et conteneurs
            vms = self.proxmox.nodes(self.node).qemu.get()
            lxc = self.proxmox.nodes(self.node).lxc.get()
            
            return {
                'node': {
                    'name': self.node,
                    'status': node_status.get('status'),
                    'cpu': {
                        'cores': node_status.get('cpuinfo', {}).get('cpus', 0),
                        'usage': round(node_status.get('cpu', 0) * 100, 2)
                    },
                    'memory': {
                        'total': round(node_status.get('memory', {}).get('total', 0) / 1024**3, 2),
                        'used': round(node_status.get('memory', {}).get('used', 0) / 1024**3, 2),
                        'free': round(node_status.get('memory', {}).get('free', 0) / 1024**3, 2)
                    }
                },
                'vms': {
                    'total': len(vms),
                    'running': sum(1 for vm in vms if vm.get('status') == 'running')
                },
                'containers': {
                    'total': len(lxc),
                    'running': sum(1 for ct in lxc if ct.get('status') == 'running')
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération ressources: {e}")
            return {'error': str(e)}
    
    def get_vm_status(self, node, vmid):
        """Récupère le statut d'une VM"""
        try:
            if not self.proxmox:
                return None
            
            status = self.proxmox.nodes(node).qemu(vmid).status.current.get()
            return status
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération statut VM {vmid}: {e}")
            return None
    
    def start_vm(self, node, vmid):
        """Démarre une VM"""
        try:
            if not self.proxmox:
                return False
            
            self.proxmox.nodes(node).qemu(vmid).status.start.post()
            logger.info(f"✅ VM {vmid} démarrée")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur démarrage VM {vmid}: {e}")
            return False
    
    def stop_vm(self, node, vmid):
        """Arrête une VM"""
        try:
            if not self.proxmox:
                return False
            
            self.proxmox.nodes(node).qemu(vmid).status.stop.post()
            logger.info(f"✅ VM {vmid} arrêtée")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur arrêt VM {vmid}: {e}")
            return False
    
    def restart_vm(self, node, vmid):
        """Redémarre une VM"""
        try:
            if not self.proxmox:
                return False
            
            self.proxmox.nodes(node).qemu(vmid).status.reboot.post()
            logger.info(f"✅ VM {vmid} redémarrée")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur redémarrage VM {vmid}: {e}")
            return False
    
    def delete_vm(self, node, vmid):
        """Supprime une VM"""
        try:
            if not self.proxmox:
                return False
            
            # Arrêter d'abord si en cours d'exécution
            status = self.get_vm_status(node, vmid)
            if status and status.get('status') == 'running':
                self.stop_vm(node, vmid)
            
            # Supprimer
            self.proxmox.nodes(node).qemu(vmid).delete()
            logger.info(f"✅ VM {vmid} supprimée")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur suppression VM {vmid}: {e}")
            return False
