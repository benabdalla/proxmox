"""
Tests pour les validateurs
"""

import pytest
from backend.utils.validators import (
    validate_deployment_request,
    is_valid_github_url,
    is_valid_name,
    extract_repo_info
)

class TestGitHubURLValidation:
    """Tests de validation d'URL GitHub"""
    
    def test_valid_github_url_with_git(self):
        assert is_valid_github_url("https://github.com/user/repo.git") == True
    
    def test_valid_github_url_without_git(self):
        assert is_valid_github_url("https://github.com/user/repo") == True
    
    def test_invalid_gitlab_url(self):
        assert is_valid_github_url("https://gitlab.com/user/repo") == False
    
    def test_invalid_url_format(self):
        assert is_valid_github_url("not-a-url") == False
    
    def test_invalid_github_url_missing_user(self):
        assert is_valid_github_url("https://github.com/repo") == False

class TestNameValidation:
    """Tests de validation de nom"""
    
    def test_valid_name_alphanumeric(self):
        assert is_valid_name("myapp123") == True
    
    def test_valid_name_with_dash(self):
        assert is_valid_name("my-app") == True
    
    def test_valid_name_with_underscore(self):
        assert is_valid_name("my_app") == True
    
    def test_invalid_name_with_space(self):
        assert is_valid_name("my app") == False
    
    def test_invalid_name_with_special_chars(self):
        assert is_valid_name("my@app") == False

class TestDeploymentRequestValidation:
    """Tests de validation de requête de déploiement"""
    
    def test_valid_request(self):
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
    
    def test_missing_required_field(self):
        data = {
            "type": "vm",
            "framework": "django"
        }
        is_valid, error = validate_deployment_request(data)
        assert is_valid == False
        assert "github_url" in error
    
    def test_invalid_type(self):
        data = {
            "type": "invalid",
            "framework": "django",
            "github_url": "https://github.com/user/repo.git"
        }
        is_valid, error = validate_deployment_request(data)
        assert is_valid == False
        assert "Type" in error
    
    def test_invalid_framework(self):
        data = {
            "type": "vm",
            "framework": "invalid",
            "github_url": "https://github.com/user/repo.git"
        }
        is_valid, error = validate_deployment_request(data)
        assert is_valid == False
        assert "Framework" in error
    
    def test_invalid_cpu(self):
        data = {
            "type": "vm",
            "framework": "django",
            "github_url": "https://github.com/user/repo.git",
            "cpu": 100
        }
        is_valid, error = validate_deployment_request(data)
        assert is_valid == False
        assert "CPU" in error

class TestRepoInfoExtraction:
    """Tests d'extraction d'informations de dépôt"""
    
    def test_extract_repo_info(self):
        info = extract_repo_info("https://github.com/django/django.git")
        assert info == {
            'owner': 'django',
            'repo': 'django'
        }
    
    def test_extract_repo_info_without_git(self):
        info = extract_repo_info("https://github.com/facebook/react")
        assert info == {
            'owner': 'facebook',
            'repo': 'react'
        }
    
    def test_extract_repo_info_invalid_url(self):
        info = extract_repo_info("https://invalid.com/user/repo")
        assert info is None
