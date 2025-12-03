"""
Fichier de configuration pour pytest
"""

import sys
import os

# Ajouter le répertoire backend au path Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

import pytest
from backend.app import create_app
from backend.models.database import db

@pytest.fixture
def app():
    """Fixture pour l'application Flask"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """Fixture pour le client de test"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Fixture pour le runner CLI"""
    return app.test_cli_runner()
