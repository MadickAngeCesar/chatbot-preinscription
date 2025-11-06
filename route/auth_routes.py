"""
Routes d'authentification
Gère les routes HTTP pour l'authentification (délègue aux contrôleurs)
"""

from flask import Blueprint, jsonify
from controllers import auth_controller
from middleware import validate_json, login_required

# Créer le Blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# ============================================
# ROUTES - AUTHENTIFICATION
# ============================================

@auth_bp.route('/register', methods=['POST'])
@validate_json('nom', 'prenom', 'email', 'password')
def register():
    """
    POST /api/auth/register
    Inscription d'un nouvel utilisateur
    
    Body (JSON):
        {
            "nom": "string",
            "prenom": "string",
            "email": "string",
            "telephone": "string (optional)",
            "password": "string",
            "role": "string (optional, default: etudiant)"
        }
    
    Response:
        {
            "success": true,
            "message": "Inscription réussie",
            "user": {
                "id": 1,
                "nom": "...",
                "prenom": "...",
                "email": "...",
                "role": "..."
            }
        }
    """
    response_data, status_code = auth_controller.register_user()
    return jsonify(response_data), status_code


@auth_bp.route('/login', methods=['POST'])
@validate_json('email', 'password')
def login():
    """
    POST /api/auth/login
    Connexion d'un utilisateur
    
    Body (JSON):
        {
            "email": "string",
            "password": "string"
        }
    
    Response:
        {
            "success": true,
            "message": "Connexion réussie",
            "user": { ... }
        }
    """
    response_data, status_code = auth_controller.login_user()
    return jsonify(response_data), status_code


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """
    POST /api/auth/logout
    Déconnexion de l'utilisateur courant
    
    Response:
        {
            "success": true,
            "message": "Déconnexion réussie"
        }
    """
    response_data, status_code = auth_controller.logout_user()
    return jsonify(response_data), status_code


# ============================================
# ROUTES - PROFIL UTILISATEUR
# ============================================

@auth_bp.route('/profile', methods=['GET'])
@login_required
def get_profile():
    """
    GET /api/auth/profile
    Récupère le profil de l'utilisateur connecté
    
    Headers:
        Cookie: session
    
    Response:
        {
            "success": true,
            "user": { ... }
        }
    """
    response_data, status_code = auth_controller.get_user_profile()
    return jsonify(response_data), status_code


@auth_bp.route('/profile', methods=['PUT'])
@login_required
@validate_json()
def update_profile():
    """
    PUT /api/auth/profile
    Met à jour le profil de l'utilisateur connecté
    
    Headers:
        Cookie: session
    
    Body (JSON):
        {
            "nom": "string (optional)",
            "prenom": "string (optional)",
            "telephone": "string (optional)"
        }
    
    Response:
        {
            "success": true,
            "message": "Profil mis à jour avec succès",
            "user": { ... }
        }
    """
    response_data, status_code = auth_controller.update_user_profile()
    return jsonify(response_data), status_code


@auth_bp.route('/change-password', methods=['POST'])
@login_required
@validate_json('current_password', 'new_password')
def change_password():
    """
    POST /api/auth/change-password
    Change le mot de passe de l'utilisateur connecté
    
    Headers:
        Cookie: session
    
    Body (JSON):
        {
            "current_password": "string",
            "new_password": "string"
        }
    
    Response:
        {
            "success": true,
            "message": "Mot de passe changé avec succès"
        }
    """
    response_data, status_code = auth_controller.change_password()
    return jsonify(response_data), status_code
