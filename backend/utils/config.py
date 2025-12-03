"""
Configuration de l'application
"""

import os

class Config:
    """Configuration globale"""
    
    # Proxmox
    PROXMOX_API_URL = os.getenv('PROXMOX_API_URL')
    PROXMOX_API_TOKEN_ID = os.getenv('PROXMOX_API_TOKEN_ID')
    PROXMOX_API_TOKEN_SECRET = os.getenv('PROXMOX_API_TOKEN_SECRET')
    PROXMOX_NODE = os.getenv('PROXMOX_NODE', 'pve')
    PROXMOX_STORAGE = os.getenv('PROXMOX_STORAGE', 'local-lvm')
    PROXMOX_BRIDGE = os.getenv('PROXMOX_BRIDGE', 'vmbr0')
    
    # Flask
    FLASK_SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')
    FLASK_ENV = os.getenv('FLASK_ENV', 'production')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
    
    # Base de données
    DATABASE_PATH = os.getenv('DATABASE_PATH', './data/deployments.db')
    
    # Réseau
    NETWORK_POOL_START = os.getenv('NETWORK_POOL_START', '192.168.1.100')
    NETWORK_POOL_END = os.getenv('NETWORK_POOL_END', '192.168.1.200')
    NETWORK_GATEWAY = os.getenv('NETWORK_GATEWAY', '192.168.1.1')
    NETWORK_NETMASK = os.getenv('NETWORK_NETMASK', '24')
    DNS_SERVERS = os.getenv('DNS_SERVERS', '8.8.8.8,8.8.4.4')
    
    # Terraform
    TERRAFORM_WORK_DIR = os.getenv('TERRAFORM_WORK_DIR', './terraform/workspaces')
    TERRAFORM_STATE_DIR = os.getenv('TERRAFORM_STATE_DIR', './terraform/states')
    
    # Logs
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', './logs/app.log')
    
    # Limites
    MAX_CPU_CORES = int(os.getenv('MAX_CPU_CORES', 8))
    MAX_MEMORY_MB = int(os.getenv('MAX_MEMORY_MB', 16384))
    MAX_DISK_GB = int(os.getenv('MAX_DISK_GB', 500))
    
    # Timeouts
    DEPLOYMENT_TIMEOUT = int(os.getenv('DEPLOYMENT_TIMEOUT', 1800))
    VM_START_TIMEOUT = int(os.getenv('VM_START_TIMEOUT', 300))
    
    # Frameworks supportés
    SUPPORTED_FRAMEWORKS = {
        'django': {'language': 'python', 'port': 8000},
        'flask': {'language': 'python', 'port': 5000},
        'fastapi': {'language': 'python', 'port': 8000},
        'nodejs': {'language': 'javascript', 'port': 3000},
        'express': {'language': 'javascript', 'port': 3000},
        'react': {'language': 'javascript', 'port': 3000},
        'vue': {'language': 'javascript', 'port': 8080},
        'nextjs': {'language': 'javascript', 'port': 3000},
        'laravel': {'language': 'php', 'port': 8000},
        'symfony': {'language': 'php', 'port': 8000},
        'springboot': {'language': 'java', 'port': 8080}
    }
    
    @classmethod
    def is_framework_supported(cls, framework):
        """Vérifie si un framework est supporté"""
        return framework.lower() in cls.SUPPORTED_FRAMEWORKS
    
    @classmethod
    def get_framework_info(cls, framework):
        """Récupère les informations d'un framework"""
        return cls.SUPPORTED_FRAMEWORKS.get(framework.lower())
