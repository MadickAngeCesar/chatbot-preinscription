"""
Middleware de validation des requêtes
Valide les données JSON et les paramètres
"""

from flask import request, jsonify
from functools import wraps
import re

# ============================================
# VALIDATORS
# ============================================

def validate_email(email):
    """Valide le format d'un email selon RFC 5322"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password):
    """
    Valide la force d'un mot de passe
    - Minimum 8 caractères
    - Au moins 1 majuscule
    - Au moins 1 minuscule
    - Au moins 1 chiffre
    """
    if len(password) < 8:
        return False, "Le mot de passe doit contenir au moins 8 caractères"
    if not re.search(r'[A-Z]', password):
        return False, "Le mot de passe doit contenir au moins une majuscule"
    if not re.search(r'[a-z]', password):
        return False, "Le mot de passe doit contenir au moins une minuscule"
    if not re.search(r'\d', password):
        return False, "Le mot de passe doit contenir au moins un chiffre"
    return True, "Mot de passe valide"


def validate_phone(phone):
    """Valide un numéro de téléphone camerounais"""
    # Format: +237 6XX XXX XXX ou 6XX XXX XXX
    pattern = r'^(\+237)?[6][0-9]{8}$'
    cleaned = phone.replace(' ', '').replace('-', '')
    return re.match(pattern, cleaned) is not None


def sanitize_string(text, max_length=None):
    """Nettoie une chaîne de caractères"""
    if not text:
        return text
    
    # Supprimer les espaces en début et fin
    text = text.strip()
    
    # Limiter la longueur
    if max_length and len(text) > max_length:
        text = text[:max_length]
    
    return text


# ============================================
# DECORATORS DE VALIDATION
# ============================================

def validate_json(*required_fields):
    """
    Décorateur pour valider les champs JSON requis
    Usage: @validate_json('email', 'password')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Vérifier le Content-Type
            if not request.is_json:
                return jsonify({
                    'success': False,
                    'error': 'Content-Type doit être application/json',
                    'code': 'INVALID_CONTENT_TYPE'
                }), 400
            
            data = request.get_json()
            
            # Vérifier les champs requis
            missing_fields = [field for field in required_fields if field not in data or not data[field]]
            
            if missing_fields:
                return jsonify({
                    'success': False,
                    'error': f'Champs requis manquants: {", ".join(missing_fields)}',
                    'code': 'MISSING_FIELDS',
                    'missing_fields': missing_fields
                }), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def validate_query_params(*required_params):
    """
    Décorateur pour valider les paramètres de requête GET
    Usage: @validate_query_params('page', 'per_page')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            missing_params = [param for param in required_params if param not in request.args]
            
            if missing_params:
                return jsonify({
                    'success': False,
                    'error': f'Paramètres requis manquants: {", ".join(missing_params)}',
                    'code': 'MISSING_PARAMS',
                    'missing_params': missing_params
                }), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def validate_file_upload(allowed_extensions=None, max_size_mb=5):
    """
    Décorateur pour valider les fichiers uploadés
    Usage: @validate_file_upload(allowed_extensions={'pdf', 'jpg', 'png'}, max_size_mb=5)
    """
    if allowed_extensions is None:
        allowed_extensions = {'pdf', 'jpg', 'jpeg', 'png'}
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Vérifier la présence de fichiers
            if not request.files:
                return jsonify({
                    'success': False,
                    'error': 'Aucun fichier fourni',
                    'code': 'NO_FILE'
                }), 400
            
            # Valider chaque fichier
            for file_key, file in request.files.items():
                if file.filename == '':
                    continue
                
                # Vérifier l'extension
                if '.' not in file.filename:
                    return jsonify({
                        'success': False,
                        'error': f'Le fichier {file_key} n\'a pas d\'extension',
                        'code': 'NO_EXTENSION'
                    }), 400
                
                ext = file.filename.rsplit('.', 1)[1].lower()
                if ext not in allowed_extensions:
                    return jsonify({
                        'success': False,
                        'error': f'Extension {ext} non autorisée pour {file_key}',
                        'code': 'INVALID_EXTENSION',
                        'allowed_extensions': list(allowed_extensions)
                    }), 400
                
                # Vérifier la taille (approximative via content_length)
                if file.content_length and file.content_length > max_size_mb * 1024 * 1024:
                    return jsonify({
                        'success': False,
                        'error': f'Le fichier {file_key} dépasse {max_size_mb}MB',
                        'code': 'FILE_TOO_LARGE'
                    }), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# ============================================
# VALIDATION MIDDLEWARE GLOBAL
# ============================================

def init_validation_middleware(app):
    """
    Initialise le middleware de validation pour l'application
    """
    
    @app.before_request
    def validate_request_size():
        """Valide la taille de la requête"""
        max_content_length = app.config.get('MAX_CONTENT_LENGTH', 5 * 1024 * 1024)
        
        if request.content_length and request.content_length > max_content_length:
            return jsonify({
                'success': False,
                'error': 'Requête trop volumineuse',
                'code': 'REQUEST_TOO_LARGE',
                'max_size_mb': max_content_length / (1024 * 1024)
            }), 413
    
    print("✅ Middleware de validation initialisé")
