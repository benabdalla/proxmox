"""
Service Terraform pour gérer l'infrastructure
"""

import os
import logging
import json
from python_terraform import Terraform, IsFlagged

logger = logging.getLogger(__name__)

class TerraformService:
    """Service pour gérer Terraform"""
    
    def __init__(self):
        self.work_dir = os.getenv('TERRAFORM_WORK_DIR', './terraform/workspaces')
        self.state_dir = os.getenv('TERRAFORM_STATE_DIR', './terraform/states')
        os.makedirs(self.work_dir, exist_ok=True)
        os.makedirs(self.state_dir, exist_ok=True)
    
    def create_workspace(self, deployment):
        """Crée un workspace Terraform pour le déploiement"""
        workspace_dir = os.path.join(self.work_dir, f"deployment-{deployment.id}")
        os.makedirs(workspace_dir, exist_ok=True)
        
        # Générer le fichier main.tf
        self._generate_main_tf(workspace_dir, deployment)
        
        # Générer le fichier variables.tf
        self._generate_variables_tf(workspace_dir)
        
        # Générer le fichier terraform.tfvars
        self._generate_tfvars(workspace_dir, deployment)
        
        # Initialiser Terraform
        tf = Terraform(working_dir=workspace_dir)
        return_code, stdout, stderr = tf.init()
        
        if return_code != 0:
            logger.error(f"Erreur init Terraform: {stderr}")
            raise RuntimeError(f"Terraform init failed: {stderr}")
        
        logger.info(f"✅ Workspace Terraform créé: {workspace_dir}")
        return workspace_dir
    
    def _generate_main_tf(self, workspace_dir, deployment):
        """Génère le fichier main.tf"""
        
        if deployment.type == 'vm':
            template = self._get_vm_template(deployment)
        else:
            template = self._get_lxc_template(deployment)
        
        with open(os.path.join(workspace_dir, 'main.tf'), 'w', encoding='utf-8') as f:
            f.write(template)
    
    def _get_vm_template(self, deployment):
        """Template Terraform pour une VM"""
        return f'''terraform {{
  required_providers {{
    proxmox = {{
      source  = "telmate/proxmox"
      version = "2.9.14"
    }}
  }}
}}

provider "proxmox" {{
  pm_api_url          = var.proxmox_api_url
  pm_api_token_id     = var.proxmox_api_token_id
  pm_api_token_secret = var.proxmox_api_token_secret
  pm_tls_insecure     = true
}}

resource "proxmox_vm_qemu" "vm" {{
  name        = var.vm_name
  target_node = var.proxmox_node
  
  # Clone depuis un template (Ubuntu 22.04 recommandé)
  clone = var.template_name
  
  # Configuration CPU et RAM
  cores   = var.cpu_cores
  sockets = 1
  memory  = var.memory_mb
  
  # Disque
  disk {{
    size    = "${{var.disk_gb}}G"
    storage = var.storage
    type    = "scsi"
  }}
  
  # Réseau
  network {{
    model  = "virtio"
    bridge = var.network_bridge
  }}
  
  # Cloud-init
  os_type   = "cloud-init"
  ipconfig0 = "ip=dhcp"
  
  # SSH
  sshkeys = var.ssh_public_key
  
  # Démarrage automatique
  automatic_reboot = true
  
  lifecycle {{
    ignore_changes = [
      network,
    ]
  }}
}}

output "vm_id" {{
  value = proxmox_vm_qemu.vm.vmid
}}

output "ip_address" {{
  value = proxmox_vm_qemu.vm.default_ipv4_address
}}
'''
    
    def _get_lxc_template(self, deployment):
        """Template Terraform pour un conteneur LXC"""
        return f'''terraform {{
  required_providers {{
    proxmox = {{
      source  = "telmate/proxmox"
      version = "2.9.14"
    }}
  }}
}}

provider "proxmox" {{
  pm_api_url          = var.proxmox_api_url
  pm_api_token_id     = var.proxmox_api_token_id
  pm_api_token_secret = var.proxmox_api_token_secret
  pm_tls_insecure     = true
}}

resource "proxmox_lxc" "container" {{
  hostname    = var.vm_name
  target_node = var.proxmox_node
  ostemplate  = var.lxc_template
  
  # Ressources
  cores  = var.cpu_cores
  memory = var.memory_mb
  swap   = 512
  
  # Disque
  rootfs {{
    storage = var.storage
    size    = "${{var.disk_gb}}G"
  }}
  
  # Réseau
  network {{
    name   = "eth0"
    bridge = var.network_bridge
    ip     = "dhcp"
  }}
  
  # SSH
  ssh_public_keys = var.ssh_public_key
  
  # Privilèges
  unprivileged = true
  
  # Démarrage
  start = true
}}

output "vm_id" {{
  value = proxmox_lxc.container.vmid
}}

output "ip_address" {{
  value = proxmox_lxc.container.network[0].ip
}}
'''
    
    def _generate_variables_tf(self, workspace_dir):
        """Génère le fichier variables.tf"""
        variables = '''variable "proxmox_api_url" {
  description = "URL de l'API Proxmox"
  type        = string
}

variable "proxmox_api_token_id" {
  description = "ID du token API Proxmox"
  type        = string
}

variable "proxmox_api_token_secret" {
  description = "Secret du token API Proxmox"
  type        = string
  sensitive   = true
}

variable "proxmox_node" {
  description = "Nom du noeud Proxmox"
  type        = string
}

variable "vm_name" {
  description = "Nom de la VM ou du conteneur"
  type        = string
}

variable "cpu_cores" {
  description = "Nombre de coeurs CPU"
  type        = number
}

variable "memory_mb" {
  description = "Mémoire RAM en MB"
  type        = number
}

variable "disk_gb" {
  description = "Taille du disque en GB"
  type        = number
}

variable "storage" {
  description = "Nom du storage Proxmox"
  type        = string
}

variable "network_bridge" {
  description = "Bridge réseau"
  type        = string
}

variable "template_name" {
  description = "Nom du template pour les VMs"
  type        = string
  default     = "ubuntu-22.04-cloudinit"
}

variable "lxc_template" {
  description = "Template pour les conteneurs LXC"
  type        = string
  default     = "local:vztmpl/ubuntu-22.04-standard_22.04-1_amd64.tar.gz"
}

variable "ssh_public_key" {
  description = "Clé SSH publique"
  type        = string
  default     = ""
}
'''
        
        with open(os.path.join(workspace_dir, 'variables.tf'), 'w', encoding='utf-8') as f:
            f.write(variables)
    
    def _generate_tfvars(self, workspace_dir, deployment):
        """Génère le fichier terraform.tfvars"""
        
        # Récupérer le nom du template depuis .env ou utiliser une valeur par défaut
        template_name = os.getenv('TEMPLATE_NAME', 'ubuntu-22.04-template')
        lxc_template = os.getenv('LXC_TEMPLATE', 'local:vztmpl/ubuntu-22.04-standard_22.04-1_amd64.tar.zst')
        
        tfvars = f'''proxmox_api_url          = "{os.getenv('PROXMOX_API_URL')}"
proxmox_api_token_id     = "{os.getenv('PROXMOX_API_TOKEN_ID')}"
proxmox_api_token_secret = "{os.getenv('PROXMOX_API_TOKEN_SECRET')}"
proxmox_node             = "{os.getenv('PROXMOX_NODE')}"
vm_name                  = "{deployment.name}"
cpu_cores                = {deployment.cpu}
memory_mb                = {deployment.memory}
disk_gb                  = {deployment.disk}
storage                  = "{os.getenv('PROXMOX_STORAGE', 'local-lvm')}"
network_bridge           = "{os.getenv('PROXMOX_BRIDGE', 'vmbr0')}"
template_name            = "{template_name}"
lxc_template             = "{lxc_template}"
'''
        
        with open(os.path.join(workspace_dir, 'terraform.tfvars'), 'w', encoding='utf-8') as f:
            f.write(tfvars)
    
    def apply(self, workspace_dir):
        """Applique la configuration Terraform"""
        tf = Terraform(working_dir=workspace_dir)
        
        return_code, stdout, stderr = tf.apply(
            skip_plan=False,
            auto_approve=True
        )
        
        output = f"{stdout}\n{stderr}"
        
        if return_code != 0:
            logger.error(f"❌ Terraform apply failed: {stderr}")
            return False, output
        
        logger.info(f"✅ Terraform apply succeeded")
        return True, output
    
    def destroy(self, workspace_dir):
        """Détruit l'infrastructure Terraform"""
        tf = Terraform(working_dir=workspace_dir)
        
        return_code, stdout, stderr = tf.destroy(auto_approve=True)
        
        output = f"{stdout}\n{stderr}"
        
        if return_code != 0:
            logger.error(f"❌ Terraform destroy failed: {stderr}")
            return False, output
        
        logger.info(f"✅ Terraform destroy succeeded")
        return True, output
    
    def get_outputs(self, workspace_dir):
        """Récupère les outputs Terraform"""
        tf = Terraform(working_dir=workspace_dir)
        
        return_code, stdout, stderr = tf.output(json=IsFlagged)
        
        if return_code != 0:
            logger.error(f"❌ Terraform output failed: {stderr}")
            return {}
        
        try:
            outputs = json.loads(stdout)
            return {
                'vm_id': outputs.get('vm_id', {}).get('value'),
                'ip_address': outputs.get('ip_address', {}).get('value')
            }
        except Exception as e:
            logger.error(f"❌ Erreur parsing outputs: {e}")
            return {}
