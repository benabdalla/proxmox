# Tests de la plateforme PaaS

## Installation des dépendances de test
```bash
pip install pytest pytest-cov pytest-mock requests-mock
```

## Lancer les tests
```bash
# Tous les tests
pytest

# Avec couverture
pytest --cov=backend --cov-report=html

# Tests spécifiques
pytest tests/test_validators.py
pytest tests/test_proxmox_service.py -v
```

## Structure des tests

```
tests/
├── __init__.py
├── conftest.py              # Fixtures communes
├── test_validators.py       # Tests validation
├── test_config.py          # Tests configuration
├── test_proxmox_service.py # Tests service Proxmox
├── test_terraform_service.py # Tests service Terraform
├── test_deployment_api.py  # Tests API déploiement
└── test_status_api.py      # Tests API statut
```

## Exemple de test

```python
import pytest
from utils.validators import validate_deployment_request, is_valid_github_url

def test_valid_github_url():
    """Test validation URL GitHub valide"""
    assert is_valid_github_url("https://github.com/user/repo.git") == True
    assert is_valid_github_url("https://github.com/user/repo") == True

def test_invalid_github_url():
    """Test validation URL GitHub invalide"""
    assert is_valid_github_url("https://gitlab.com/user/repo") == False
    assert is_valid_github_url("not-a-url") == False

def test_validate_deployment_request():
    """Test validation requête déploiement"""
    data = {
        "type": "vm",
        "framework": "django",
        "github_url": "https://github.com/user/repo.git",
        "cpu": 2,
        "memory": 2048,
        "disk": 20
    }
    
    is_valid, error = validate_deployment_request(data)
    assert is_valid == True
    assert error is None

def test_validate_deployment_missing_field():
    """Test validation avec champ manquant"""
    data = {
        "type": "vm",
        "framework": "django"
        # github_url manquant
    }
    
    is_valid, error = validate_deployment_request(data)
    assert is_valid == False
    assert "github_url" in error
```

## Tests d'intégration

```python
import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        yield client

def test_health_endpoint(client):
    """Test endpoint de santé"""
    response = client.get('/health')
    assert response.status_code == 200
    assert b'healthy' in response.data

def test_create_deployment(client):
    """Test création déploiement"""
    data = {
        "type": "vm",
        "framework": "django",
        "github_url": "https://github.com/user/repo.git",
        "cpu": 2,
        "memory": 2048,
        "disk": 20
    }
    
    response = client.post('/api/deploy', json=data)
    assert response.status_code == 202
```
