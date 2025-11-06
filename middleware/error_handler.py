"""
Middleware de gestion des erreurs
Gère toutes les erreurs de l'application de manière centralisée
"""

from flask import jsonify, render_template, request
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# ============================================
# CLASSES D'ERREURS PERSONNALISÉES
# ============================================

class APIError(Exception):
    """Classe de base pour toutes les erreurs API"""
    status_code = 500
    
    def __init__(self, message, status_code=None, payload=None):
        super().__init__()
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload
    
    def to_dict(self):
        """Convertit l'erreur en dictionnaire"""
        rv = dict(self.payload or ())
        rv['error'] = self.message
        rv['status'] = self.status_code
        rv['timestamp'] = datetime.now().isoformat()
        return rv


class ValidationError(APIError):
    """Erreur de validation des données"""
    status_code = 400
    
    def __init__(self, message="Données invalides", errors=None):
        super().__init__(message, status_code=400)
        self.errors = errors or []
    
    def to_dict(self):
        rv = super().to_dict()
        if self.errors:
            rv['errors'] = self.errors
        return rv


class AuthenticationError(APIError):
    """Erreur d'authentification"""
    status_code = 401
    
    def __init__(self, message="Authentification requise"):
        super().__init__(message, status_code=401)


class AuthorizationError(APIError):
    """Erreur d'autorisation (accès refusé)"""
    status_code = 403
    
    def __init__(self, message="Accès refusé"):
        super().__init__(message, status_code=403)


class NotFoundError(APIError):
    """Ressource non trouvée"""
    status_code = 404
    
    def __init__(self, message="Ressource non trouvée"):
        super().__init__(message, status_code=404)


class DatabaseError(APIError):
    """Erreur de base de données"""
    status_code = 500
    
    def __init__(self, message="Erreur de base de données"):
        super().__init__(message, status_code=500)


# ============================================
# UTILITAIRES
# ============================================

def format_validation_errors(errors):
    """Formate les erreurs de validation de manière cohérente"""
    if isinstance(errors, dict):
        return [{"field": k, "message": v} for k, v in errors.items()]
    elif isinstance(errors, list):
        return errors
    else:
        return [{"message": str(errors)}]


def is_api_request():
    """Vérifie si la requête est une requête API"""
    return request.path.startswith('/api/') or request.headers.get('Content-Type') == 'application/json'


# ============================================
# GESTIONNAIRES D'ERREURS
# ============================================

def handle_api_error(error):
    """Gestionnaire pour les erreurs API personnalisées"""
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    logger.error(f"API Error {error.status_code}: {error.message}")
    return response


def handle_400_error(error):
    """Gestionnaire d'erreur 400 - Bad Request"""
    if is_api_request():
        return jsonify({
            'error': 'Requête invalide',
            'message': str(error),
            'status': 400,
            'timestamp': datetime.now().isoformat()
        }), 400
    return render_template('error.html', 
                         message="Requête invalide",
                         code=400), 400


def handle_401_error(error):
    """Gestionnaire d'erreur 401 - Unauthorized"""
    if is_api_request():
        return jsonify({
            'error': 'Authentification requise',
            'message': 'Vous devez être connecté pour accéder à cette ressource',
            'status': 401,
            'timestamp': datetime.now().isoformat()
        }), 401
    return render_template('error.html',
                         message="Authentification requise",
                         code=401), 401


def handle_403_error(error):
    """Gestionnaire d'erreur 403 - Forbidden"""
    if is_api_request():
        return jsonify({
            'error': 'Accès refusé',
            'message': 'Vous n\'avez pas les permissions nécessaires',
            'status': 403,
            'timestamp': datetime.now().isoformat()
        }), 403
    return render_template('error.html',
                         message="Accès refusé",
                         code=403), 403


def handle_404_error(error):
    """Gestionnaire d'erreur 404 - Not Found"""
    if is_api_request():
        return jsonify({
            'error': 'Ressource non trouvée',
            'message': 'La ressource demandée n\'existe pas',
            'status': 404,
            'timestamp': datetime.now().isoformat()
        }), 404
    return render_template('error.html',
                         message="Page non trouvée",
                         code=404), 404


def handle_405_error(error):
    """Gestionnaire d'erreur 405 - Method Not Allowed"""
    if is_api_request():
        return jsonify({
            'error': 'Méthode non autorisée',
            'message': f'La méthode {request.method} n\'est pas autorisée pour cette URL',
            'status': 405,
            'timestamp': datetime.now().isoformat()
        }), 405
    return render_template('error.html',
                         message="Méthode non autorisée",
                         code=405), 405


def handle_413_error(error):
    """Gestionnaire d'erreur 413 - Request Entity Too Large"""
    if is_api_request():
        return jsonify({
            'error': 'Fichier trop volumineux',
            'message': 'Le fichier envoyé dépasse la taille maximale autorisée (5MB)',
            'status': 413,
            'timestamp': datetime.now().isoformat()
        }), 413
    return render_template('error.html',
                         message="Fichier trop volumineux",
                         code=413), 413


def handle_429_error(error):
    """Gestionnaire d'erreur 429 - Too Many Requests"""
    if is_api_request():
        return jsonify({
            'error': 'Trop de requêtes',
            'message': 'Vous avez effectué trop de requêtes. Veuillez réessayer plus tard.',
            'status': 429,
            'timestamp': datetime.now().isoformat()
        }), 429
    return render_template('error.html',
                         message="Trop de requêtes",
                         code=429), 429


def handle_500_error(error):
    """Gestionnaire d'erreur 500 - Internal Server Error"""
    logger.error(f"Internal Server Error: {str(error)}", exc_info=True)
    if is_api_request():
        return jsonify({
            'error': 'Erreur interne du serveur',
            'message': 'Une erreur inattendue s\'est produite',
            'status': 500,
            'timestamp': datetime.now().isoformat()
        }), 500
    return render_template('error.html',
                         message="Erreur interne du serveur",
                         code=500), 500


def handle_503_error(error):
    """Gestionnaire d'erreur 503 - Service Unavailable"""
    if is_api_request():
        return jsonify({
            'error': 'Service indisponible',
            'message': 'Le service est temporairement indisponible',
            'status': 503,
            'timestamp': datetime.now().isoformat()
        }), 503
    return render_template('error.html',
                         message="Service indisponible",
                         code=503), 503


def handle_generic_error(error):
    """Gestionnaire d'erreur générique"""
    logger.error(f"Unhandled error: {str(error)}", exc_info=True)
    if is_api_request():
        return jsonify({
            'error': 'Erreur',
            'message': str(error),
            'status': 500,
            'timestamp': datetime.now().isoformat()
        }), 500
    return render_template('error.html',
                         message="Une erreur s'est produite",
                         code=500), 500


# ============================================
# INITIALISATION
# ============================================

def init_error_handlers(app):
    """Initialise tous les gestionnaires d'erreurs pour l'application Flask"""
    
    # Enregistrer les gestionnaires pour les erreurs personnalisées
    app.register_error_handler(APIError, handle_api_error)
    app.register_error_handler(ValidationError, handle_api_error)
    app.register_error_handler(AuthenticationError, handle_api_error)
    app.register_error_handler(AuthorizationError, handle_api_error)
    app.register_error_handler(NotFoundError, handle_api_error)
    app.register_error_handler(DatabaseError, handle_api_error)
    
    # Enregistrer les gestionnaires pour les codes HTTP
    app.register_error_handler(400, handle_400_error)
    app.register_error_handler(401, handle_401_error)
    app.register_error_handler(403, handle_403_error)
    app.register_error_handler(404, handle_404_error)
    app.register_error_handler(405, handle_405_error)
    app.register_error_handler(413, handle_413_error)
    app.register_error_handler(429, handle_429_error)
    app.register_error_handler(500, handle_500_error)
    app.register_error_handler(503, handle_503_error)
    
    # Gestionnaire d'erreur générique
    app.register_error_handler(Exception, handle_generic_error)
    
    logger.info("Gestionnaires d'erreurs initialises avec succes")
