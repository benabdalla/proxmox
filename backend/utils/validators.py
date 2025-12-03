"""
Validateurs pour les requêtes API
"""

import re
from utils.config import Config

def validate_deployment_request(data):
    """
    Valide une requête de déploiement
    
    Args:
        data: Dictionnaire contenant les données de déploiement
        
    Returns:
        Tuple (is_valid, error_message)
    """
    
    # Champs obligatoires
    required_fields = ['type', 'framework', 'github_url']
    for field in required_fields:
        if field not in data:
            return False, f"Champ obligatoire manquant: {field}"
    
    # Type de déploiement
    if data['type'] not in ['vm', 'lxc']:
        return False, "Type doit être 'vm' ou 'lxc'"
    
    # Framework
    if not Config.is_framework_supported(data['framework']):
        return False, f"Framework non supporté: {data['framework']}"
    
    # URL GitHub
    github_url = data['github_url']
    if not is_valid_github_url(github_url):
        return False, "URL GitHub invalide"
    
    # Ressources CPU
    cpu = data.get('cpu', 2)
    if not isinstance(cpu, int) or cpu < 1 or cpu > Config.MAX_CPU_CORES:
        return False, f"CPU doit être entre 1 et {Config.MAX_CPU_CORES}"
    
    # Ressources Mémoire
    memory = data.get('memory', 2048)
    if not isinstance(memory, int) or memory < 512 or memory > Config.MAX_MEMORY_MB:
        return False, f"Mémoire doit être entre 512 et {Config.MAX_MEMORY_MB} MB"
    
    # Ressources Disque
    disk = data.get('disk', 20)
    if not isinstance(disk, int) or disk < 10 or disk > Config.MAX_DISK_GB:
        return False, f"Disque doit être entre 10 et {Config.MAX_DISK_GB} GB"
    
    # Nom (optionnel)
    name = data.get('name', '')
    if name and not is_valid_name(name):
        return False, "Nom invalide (caractères alphanumériques et tirets uniquement)"
    
    return True, None

def is_valid_github_url(url):
    """Valide une URL GitHub"""
    pattern = r'^https://github\.com/[\w-]+/[\w.-]+(?:\.git)?$'
    return bool(re.match(pattern, url))

def is_valid_name(name):
    """Valide un nom de déploiement"""
    pattern = r'^[a-zA-Z0-9-_]+$'
    return bool(re.match(pattern, name)) and len(name) <= 100

def sanitize_github_url(url):
    """Nettoie une URL GitHub"""
    # Retirer .git à la fin si présent
    if url.endswith('.git'):
        url = url[:-4]
    return url

def extract_repo_info(github_url):
    """Extrait les informations d'un dépôt GitHub"""
    # https://github.com/user/repo
    pattern = r'https://github\.com/([\w-]+)/([\w.-]+)'
    match = re.match(pattern, github_url)
    
    if match:
        return {
            'owner': match.group(1),
            'repo': match.group(2).replace('.git', '')
        }
    
    return None
