"""Initialisation du package api"""
from .deployment import deployment_bp
from .status import status_bp

__all__ = ['deployment_bp', 'status_bp']
