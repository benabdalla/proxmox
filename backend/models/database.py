"""
Modèles de base de données SQLAlchemy
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    """Initialise la base de données"""
    db.init_app(app)
    with app.app_context():
        db.create_all()

class Deployment(db.Model):
    """Modèle pour un déploiement"""
    __tablename__ = 'deployments'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(10), nullable=False)  # vm ou lxc
    framework = db.Column(db.String(50), nullable=False)
    github_url = db.Column(db.String(500), nullable=False)
    
    # Ressources
    cpu = db.Column(db.Integer, nullable=False)
    memory = db.Column(db.Integer, nullable=False)  # en MB
    disk = db.Column(db.Integer, nullable=False)  # en GB
    
    # Proxmox
    proxmox_id = db.Column(db.Integer)
    proxmox_node = db.Column(db.String(50))
    ip_address = db.Column(db.String(15))
    
    # État
    status = db.Column(db.String(20), default='pending')  # pending, creating, running, failed, stopped, deleted
    error_message = db.Column(db.Text)
    
    # Métadonnées
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deployed_at = db.Column(db.DateTime)
    
    # Logs
    terraform_output = db.Column(db.Text)
    deployment_log = db.Column(db.Text)
    
    def to_dict(self):
        """Convertit le déploiement en dictionnaire"""
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'framework': self.framework,
            'github_url': self.github_url,
            'resources': {
                'cpu': self.cpu,
                'memory': self.memory,
                'disk': self.disk
            },
            'proxmox': {
                'id': self.proxmox_id,
                'node': self.proxmox_node,
                'ip': self.ip_address
            },
            'status': self.status,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'deployed_at': self.deployed_at.isoformat() if self.deployed_at else None
        }

    def __repr__(self):
        return f'<Deployment {self.id}: {self.name} ({self.status})>'
