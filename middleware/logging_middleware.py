"""
Middleware de logging et monitoring
Enregistre les requêtes, réponses et erreurs
"""

from flask import request, g
from datetime import datetime
import logging
import json
import time
import os

# Ensure logs directory exists (use project root so relative runs and deployed runs work)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
LOG_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, 'app.log')

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# ============================================
# MIDDLEWARE DE LOGGING
# ============================================

def init_logging_middleware(app):
    """
    Initialise le middleware de logging pour l'application
    """
    
    @app.before_request
    def log_request_info():
        """Log les informations de la requête entrante"""
        g.start_time = time.time()
        
        # Informations de base
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'method': request.method,
            'path': request.path,
            'ip': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', 'Unknown')
        }
        
        # Ajouter l'utilisateur si authentifié
        if hasattr(g, 'user_id') and g.user_id:
            log_data['user_id'] = g.user_id
            log_data['user_role'] = g.user_role
        
        # Ajouter les paramètres de requête (sans les mots de passe)
        if request.args:
            log_data['query_params'] = dict(request.args)
        
        # Pour les requêtes POST/PUT, logger le body (sans données sensibles)
        if request.method in ['POST', 'PUT', 'PATCH'] and request.is_json:
            try:
                data = request.get_json()
                # Masquer les données sensibles
                safe_data = {k: '***' if k in ['password', 'password_hash', 'token'] else v 
                           for k, v in data.items()}
                log_data['body'] = safe_data
            except:
                pass
        
        # Logger avec niveau approprié
        if request.path.startswith('/api/'):
            logger.info(f"API Request: {json.dumps(log_data)}")
        else:
            logger.debug(f"Request: {json.dumps(log_data)}")
    
    @app.after_request
    def log_response_info(response):
        """Log les informations de la réponse"""
        # Calculer le temps de traitement
        if hasattr(g, 'start_time'):
            elapsed_time = time.time() - g.start_time
            
            log_data = {
                'timestamp': datetime.now().isoformat(),
                'method': request.method,
                'path': request.path,
                'status_code': response.status_code,
                'elapsed_time_ms': round(elapsed_time * 1000, 2),
                'content_type': response.content_type
            }
            
            # Ajouter l'utilisateur si disponible
            if hasattr(g, 'user_id') and g.user_id:
                log_data['user_id'] = g.user_id
            
            # Niveau de log selon le status code
            if response.status_code >= 500:
                logger.error(f"Response: {json.dumps(log_data)}")
            elif response.status_code >= 400:
                logger.warning(f"Response: {json.dumps(log_data)}")
            elif request.path.startswith('/api/'):
                logger.info(f"Response: {json.dumps(log_data)}")
            else:
                logger.debug(f"Response: {json.dumps(log_data)}")
        
        return response
    
    print("✅ Middleware de logging initialisé")


# ============================================
# FONCTIONS UTILITAIRES DE LOGGING
# ============================================

def log_auth_attempt(email, success, reason=None):
    """Log une tentative d'authentification"""
    log_data = {
        'timestamp': datetime.now().isoformat(),
        'event': 'AUTH_ATTEMPT',
        'email': email,
        'success': success,
        'ip': request.remote_addr
    }
    
    if not success and reason:
        log_data['reason'] = reason
    
    if success:
        logger.info(f"Auth Success: {json.dumps(log_data)}")
    else:
        logger.warning(f"Auth Failed: {json.dumps(log_data)}")


def log_user_action(action, user_id, details=None):
    """Log une action utilisateur importante"""
    log_data = {
        'timestamp': datetime.now().isoformat(),
        'event': 'USER_ACTION',
        'action': action,
        'user_id': user_id,
        'ip': request.remote_addr
    }
    
    if details:
        log_data['details'] = details
    
    logger.info(f"User Action: {json.dumps(log_data)}")


def log_security_event(event_type, severity='INFO', details=None):
    """Log un événement de sécurité"""
    log_data = {
        'timestamp': datetime.now().isoformat(),
        'event': 'SECURITY_EVENT',
        'type': event_type,
        'severity': severity,
        'ip': request.remote_addr,
        'path': request.path
    }
    
    if details:
        log_data['details'] = details
    
    if severity == 'CRITICAL':
        logger.critical(f"Security: {json.dumps(log_data)}")
    elif severity == 'ERROR':
        logger.error(f"Security: {json.dumps(log_data)}")
    elif severity == 'WARNING':
        logger.warning(f"Security: {json.dumps(log_data)}")
    else:
        logger.info(f"Security: {json.dumps(log_data)}")


def log_database_error(operation, error, query=None):
    """Log une erreur de base de données"""
    log_data = {
        'timestamp': datetime.now().isoformat(),
        'event': 'DATABASE_ERROR',
        'operation': operation,
        'error': str(error),
        'path': request.path
    }
    
    if query:
        log_data['query'] = query
    
    logger.error(f"Database Error: {json.dumps(log_data)}")
