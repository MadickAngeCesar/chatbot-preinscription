"""
Middleware d'authentification
Gère la vérification des sessions et des permissions
"""

from flask import session, request, jsonify, g
from functools import wraps
from datetime import datetime, timedelta
import sqlite3

DATABASE = 'database/chatbot.db'

def get_db_connection():
    """Crée une connexion à la base de données"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# ============================================
# DECORATORS D'AUTHENTIFICATION
# ============================================

def login_required(f):
    """
    Décorateur pour protéger les routes nécessitant une authentification
    Vérifie la présence d'une session valide
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({
                'success': False,
                'error': 'Authentification requise',
                'code': 'AUTH_REQUIRED'
            }), 401
        
        # Vérifier l'expiration de la session
        last_activity = session.get('last_activity')
        if last_activity:
            last_activity_time = datetime.fromisoformat(last_activity)
            if datetime.now() - last_activity_time > timedelta(hours=24):
                session.clear()
                return jsonify({
                    'success': False,
                    'error': 'Session expirée',
                    'code': 'SESSION_EXPIRED'
                }), 401
        
        # Mettre à jour l'activité
        session['last_activity'] = datetime.now().isoformat()
        
        # Charger les informations utilisateur dans g
        g.user_id = session['user_id']
        g.user_email = session.get('email')
        g.user_role = session.get('role', 'visiteur')
        
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """
    Décorateur pour protéger les routes réservées aux administrateurs
    Nécessite d'abord d'être authentifié
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({
                'success': False,
                'error': 'Authentification requise',
                'code': 'AUTH_REQUIRED'
            }), 401
        
        if session.get('role') != 'admin':
            return jsonify({
                'success': False,
                'error': 'Accès réservé aux administrateurs',
                'code': 'ADMIN_REQUIRED'
            }), 403
        
        # Charger les informations utilisateur dans g
        g.user_id = session['user_id']
        g.user_email = session.get('email')
        g.user_role = session['role']
        
        return f(*args, **kwargs)
    return decorated_function


def role_required(*allowed_roles):
    """
    Décorateur pour protéger les routes par rôle
    Usage: @role_required('admin', 'etudiant')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return jsonify({
                    'success': False,
                    'error': 'Authentification requise',
                    'code': 'AUTH_REQUIRED'
                }), 401
            
            user_role = session.get('role', 'visiteur')
            if user_role not in allowed_roles:
                return jsonify({
                    'success': False,
                    'error': f'Accès réservé aux rôles: {", ".join(allowed_roles)}',
                    'code': 'ROLE_REQUIRED'
                }), 403
            
            # Charger les informations utilisateur dans g
            g.user_id = session['user_id']
            g.user_email = session.get('email')
            g.user_role = user_role
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def optional_auth(f):
    """
    Décorateur pour les routes où l'authentification est optionnelle
    Charge les infos utilisateur si disponibles, sinon continue
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' in session:
            g.user_id = session.get('user_id')
            g.user_email = session.get('email')
            g.user_role = session.get('role', 'visiteur')
            g.authenticated = True
        else:
            g.user_id = None
            g.user_email = None
            g.user_role = 'visiteur'
            g.authenticated = False
        
        return f(*args, **kwargs)
    return decorated_function


# ============================================
# MIDDLEWARE DE VÉRIFICATION DE SESSION
# ============================================

def init_auth_middleware(app):
    """
    Initialise le middleware d'authentification pour l'application
    """
    
    @app.before_request
    def check_session_validity():
        """Vérifie la validité de la session avant chaque requête"""
        # Exclure les routes publiques
        public_routes = [
            '/static', '/api/auth/login', '/api/auth/register', 
            '/login', '/register', '/', '/health', '/api/health'
        ]
        
        # Vérifier si la route actuelle est publique
        if any(request.path.startswith(route) for route in public_routes):
            return None
        
        # Si une session existe, vérifier sa validité
        if 'user_id' in session:
            last_activity = session.get('last_activity')
            if last_activity:
                try:
                    last_activity_time = datetime.fromisoformat(last_activity)
                    if datetime.now() - last_activity_time > timedelta(hours=24):
                        # Session expirée
                        session.clear()
                        if request.path.startswith('/api/'):
                            return jsonify({
                                'success': False,
                                'error': 'Session expirée',
                                'code': 'SESSION_EXPIRED'
                            }), 401
                except:
                    pass
    
    @app.after_request
    def update_session_activity(response):
        """Met à jour l'activité de session après chaque requête authentifiée"""
        if 'user_id' in session and response.status_code < 400:
            session['last_activity'] = datetime.now().isoformat()
        return response
    
    print("✅ Middleware d'authentification initialisé")
