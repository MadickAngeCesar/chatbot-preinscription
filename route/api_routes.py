"""
Routes API principales
Gère les routes HTTP pour chat, préinscriptions, établissements et filières
"""

from flask import Blueprint, jsonify
from controllers import (
    chat_controller,
    preinscription_controller,
    etablissement_controller,
    filiere_controller
)
from middleware import (
    login_required,
    admin_required,
    optional_auth,
    validate_json,
    validate_file_upload
)

# Créer le Blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

# ============================================
# ROUTES - CHATBOT
# ============================================

@api_bp.route('/message', methods=['POST'])
@optional_auth
@validate_json('message')
def send_message():
    """
    POST /api/message
    Envoie un message au chatbot et récupère la réponse
    
    Body (JSON):
        {
            "message": "string",
            "session_id": "string (optional)"
        }
    
    Response:
        {
            "success": true,
            "response": "...",
            "session_id": "...",
            "timestamp": "..."
        }
    """
    response_data, status_code = chat_controller.send_message()
    return jsonify(response_data), status_code


@api_bp.route('/messages/history/<session_id>', methods=['GET'])
def get_message_history(session_id):
    """
    GET /api/messages/history/<session_id>
    Récupère l'historique des messages d'une session
    
    Response:
        {
            "success": true,
            "session_id": "...",
            "messages": [...],
            "count": 10
        }
    """
    response_data, status_code = chat_controller.get_message_history(session_id)
    return jsonify(response_data), status_code


@api_bp.route('/chat/sessions', methods=['GET'])
@login_required
def get_user_chat_sessions():
    """
    GET /api/chat/sessions
    Récupère toutes les sessions de chat de l'utilisateur connecté
    
    Response:
        {
            "success": true,
            "sessions": [...],
            "count": 5
        }
    """
    response_data, status_code = chat_controller.get_user_chat_sessions()
    return jsonify(response_data), status_code


@api_bp.route('/chat/sessions/<session_id>', methods=['DELETE'])
@login_required
def delete_chat_session(session_id):
    """
    DELETE /api/chat/sessions/<session_id>
    Supprime une session de chat
    
    Response:
        {
            "success": true,
            "message": "Session supprimée avec succès"
        }
    """
    response_data, status_code = chat_controller.delete_chat_session(session_id)
    return jsonify(response_data), status_code


# ============================================
# ROUTES - PRÉINSCRIPTIONS
# ============================================

@api_bp.route('/preinscription', methods=['POST'])
@login_required
@validate_file_upload(allowed_extensions={'pdf', 'jpg', 'jpeg', 'png'}, max_size_mb=5)
def create_preinscription():
    """
    POST /api/preinscription
    Crée une nouvelle demande de préinscription
    
    Headers:
        Content-Type: multipart/form-data
    
    Form Data:
        nom, prenom, email, telephone, dateNaissance, lieuNaissance,
        adresse, programme, niveau, motivation, acceptTerms,
        photo (file), diplome (file), releve (file), cv (file)
    
    Response:
        {
            "success": true,
            "message": "Préinscription enregistrée avec succès !",
            "preinscription_id": 1
        }
    """
    response_data, status_code = preinscription_controller.create_preinscription()
    return jsonify(response_data), status_code


@api_bp.route('/preinscriptions', methods=['GET'])
@login_required
def get_preinscriptions():
    """
    GET /api/preinscriptions
    Récupère la liste des préinscriptions
    (Admin: toutes, Utilisateur: ses propres préinscriptions)
    
    Query Params:
        - page: int (default: 1)
        - per_page: int (default: 20, max: 100)
        - statut: string (nouveau, en_cours, validé, rejeté)
        - niveau: string (Licence, Master, Doctorat)
    
    Response:
        {
            "success": true,
            "preinscriptions": [...],
            "pagination": { ... }
        }
    """
    response_data, status_code = preinscription_controller.get_preinscriptions()
    return jsonify(response_data), status_code


@api_bp.route('/preinscriptions/<int:preinscription_id>', methods=['GET'])
@login_required
def get_preinscription_detail(preinscription_id):
    """
    GET /api/preinscriptions/<id>
    Récupère les détails d'une préinscription spécifique
    
    Response:
        {
            "success": true,
            "preinscription": { ... }
        }
    """
    response_data, status_code = preinscription_controller.get_preinscription_detail(preinscription_id)
    return jsonify(response_data), status_code


@api_bp.route('/preinscriptions/<int:preinscription_id>/status', methods=['PUT'])
@admin_required
@validate_json('statut')
def update_preinscription_status(preinscription_id):
    """
    PUT /api/preinscriptions/<id>/status
    Met à jour le statut d'une préinscription (admin uniquement)
    
    Body (JSON):
        {
            "statut": "string (nouveau, en_cours, validé, rejeté)"
        }
    
    Response:
        {
            "success": true,
            "message": "Statut mis à jour avec succès"
        }
    """
    response_data, status_code = preinscription_controller.update_preinscription_status(preinscription_id)
    return jsonify(response_data), status_code


# ============================================
# ROUTES - ÉTABLISSEMENTS
# ============================================

@api_bp.route('/etablissements', methods=['GET'])
def get_etablissements():
    """
    GET /api/etablissements
    Récupère la liste de tous les établissements
    
    Query Params:
        - actif: int (0 ou 1, default: 1)
        - type: string (université, école, institut)
        - ville: string
        - page: int (default: 1)
        - per_page: int (default: 20, max: 100)
    
    Response:
        {
            "success": true,
            "data": [...],
            "pagination": { ... }
        }
    """
    response_data, status_code = etablissement_controller.get_etablissements()
    return jsonify(response_data), status_code


@api_bp.route('/etablissements/<int:etablissement_id>', methods=['GET'])
def get_etablissement_detail(etablissement_id):
    """
    GET /api/etablissements/<id>
    Récupère les détails d'un établissement spécifique
    
    Response:
        {
            "success": true,
            "data": { ... }
        }
    """
    response_data, status_code = etablissement_controller.get_etablissement_detail(etablissement_id)
    return jsonify(response_data), status_code


@api_bp.route('/etablissements/<int:etablissement_id>/stats', methods=['GET'])
@admin_required
def get_etablissement_stats(etablissement_id):
    """
    GET /api/etablissements/<id>/stats
    Récupère les statistiques d'un établissement (admin uniquement)
    
    Response:
        {
            "success": true,
            "data": {
                "etablissement": { ... },
                "statistiques": { ... }
            }
        }
    """
    response_data, status_code = etablissement_controller.get_etablissement_stats(etablissement_id)
    return jsonify(response_data), status_code


# ============================================
# ROUTES - FILIÈRES
# ============================================

@api_bp.route('/filieres', methods=['GET'])
def get_filieres():
    """
    GET /api/filieres
    Récupère la liste des filières actives
    
    Query Params:
        - etablissement_id: int
        - niveau: string (Licence, Master, Doctorat)
        - departement: string
        - page: int (default: 1)
        - per_page: int (default: 20, max: 100)
    
    Response:
        {
            "success": true,
            "data": [...],
            "pagination": { ... }
        }
    """
    response_data, status_code = filiere_controller.get_filieres()
    return jsonify(response_data), status_code


@api_bp.route('/filieres/<int:filiere_id>', methods=['GET'])
def get_filiere_detail(filiere_id):
    """
    GET /api/filieres/<id>
    Récupère les détails complets d'une filière
    
    Response:
        {
            "success": true,
            "data": { ... }
        }
    """
    response_data, status_code = filiere_controller.get_filiere_detail(filiere_id)
    return jsonify(response_data), status_code


@api_bp.route('/filieres/by-niveau', methods=['GET'])
def get_filieres_by_niveau():
    """
    GET /api/filieres/by-niveau
    Récupère les filières groupées par niveau
    
    Query Params:
        - etablissement_id: int (optional)
    
    Response:
        {
            "success": true,
            "data": {
                "Licence": [...],
                "Master": [...],
                "Doctorat": [...]
            }
        }
    """
    response_data, status_code = filiere_controller.get_filieres_by_niveau()
    return jsonify(response_data), status_code


# ============================================
# ROUTE - HEALTH CHECK
# ============================================

@api_bp.route('/health', methods=['GET'])
def health():
    """
    GET /api/health
    Vérifie que l'API fonctionne correctement
    
    Response:
        {
            "status": "healthy",
            "timestamp": "...",
            "version": "3.0.0"
        }
    """
    from datetime import datetime
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '3.0.0',
        'architecture': 'MVC with Controllers'
    }), 200
