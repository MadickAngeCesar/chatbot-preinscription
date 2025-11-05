"""
API d'authentification et gestion des utilisateurs
Chatbot de Préinscription Universitaire
Auteur: Madick Ange César
Date: Novembre 2025
"""

from flask import Blueprint, request, jsonify, session
from functools import wraps
import sqlite3
import hashlib
import secrets
import re
from datetime import datetime, timedelta

# Créer le Blueprint pour l'authentification
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# Configuration
DATABASE = 'database/chatbot.db'
SESSION_TIMEOUT = 3600  # 1 heure en secondes

def get_db_connection():
    """Crée une connexion à la base de données"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# ============================================
# UTILITAIRES
# ============================================

def hash_password(password):
    """Hashe un mot de passe avec SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def validate_email(email):
    """Valide le format d'un email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """
    Valide la force d'un mot de passe
    Minimum 8 caractères, 1 majuscule, 1 minuscule, 1 chiffre
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

def generate_session_token():
    """Génère un token de session unique"""
    return secrets.token_urlsafe(32)

def login_required(f):
    """Décorateur pour protéger les routes nécessitant une authentification"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({
                'success': False,
                'error': 'Authentification requise'
            }), 401
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Décorateur pour protéger les routes réservées aux admins"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({
                'success': False,
                'error': 'Authentification requise'
            }), 401
        
        if session.get('role') != 'admin':
            return jsonify({
                'success': False,
                'error': 'Accès réservé aux administrateurs'
            }), 403
        
        return f(*args, **kwargs)
    return decorated_function

# ============================================
# ENDPOINTS - INSCRIPTION
# ============================================

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    POST /api/auth/register
    Inscription d'un nouvel utilisateur
    
    Body:
        {
            "nom": "Dupont",
            "prenom": "Jean",
            "email": "jean@example.com",
            "telephone": "+237690000000",
            "password": "Password123",
            "confirm_password": "Password123"
        }
    """
    try:
        data = request.get_json()
        
        # Validation des champs requis
        required_fields = ['nom', 'prenom', 'email', 'password', 'confirm_password']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return jsonify({
                'success': False,
                'error': f'Champs manquants: {", ".join(missing_fields)}'
            }), 400
        
        nom = data['nom'].strip()
        prenom = data['prenom'].strip()
        email = data['email'].strip().lower()
        telephone = data.get('telephone', '').strip()
        password = data['password']
        confirm_password = data['confirm_password']
        
        # Validation de l'email
        if not validate_email(email):
            return jsonify({
                'success': False,
                'error': 'Format d\'email invalide'
            }), 400
        
        # Vérifier si l'email existe déjà
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
        if cursor.fetchone():
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Cet email est déjà utilisé'
            }), 400
        
        # Validation du mot de passe
        if password != confirm_password:
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Les mots de passe ne correspondent pas'
            }), 400
        
        is_valid, message = validate_password(password)
        if not is_valid:
            conn.close()
            return jsonify({
                'success': False,
                'error': message
            }), 400
        
        # Hasher le mot de passe
        password_hash = hash_password(password)
        
        # Insérer l'utilisateur
        cursor.execute('''
            INSERT INTO users (nom, prenom, email, telephone, password_hash, role)
            VALUES (?, ?, ?, ?, ?, 'etudiant')
        ''', (nom, prenom, email, telephone, password_hash))
        
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Inscription réussie',
            'user': {
                'id': user_id,
                'nom': nom,
                'prenom': prenom,
                'email': email,
                'role': 'etudiant'
            }
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================
# ENDPOINTS - CONNEXION
# ============================================

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    POST /api/auth/login
    Connexion d'un utilisateur
    
    Body:
        {
            "email": "jean@example.com",
            "password": "Password123"
        }
    """
    try:
        data = request.get_json()
        
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({
                'success': False,
                'error': 'Email et mot de passe requis'
            }), 400
        
        email = data['email'].strip().lower()
        password = data['password']
        
        # Rechercher l'utilisateur
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, nom, prenom, email, telephone, password_hash, role
            FROM users
            WHERE email = ?
        ''', (email,))
        
        user = cursor.fetchone()
        conn.close()
        
        if not user:
            return jsonify({
                'success': False,
                'error': 'Email ou mot de passe incorrect'
            }), 401
        
        # Vérifier le mot de passe
        password_hash = hash_password(password)
        if password_hash != user['password_hash']:
            return jsonify({
                'success': False,
                'error': 'Email ou mot de passe incorrect'
            }), 401
        
        # Créer la session
        session['user_id'] = user['id']
        session['email'] = user['email']
        session['role'] = user['role']
        session['nom'] = user['nom']
        session['prenom'] = user['prenom']
        session['login_time'] = datetime.now().isoformat()
        
        return jsonify({
            'success': True,
            'message': 'Connexion réussie',
            'user': {
                'id': user['id'],
                'nom': user['nom'],
                'prenom': user['prenom'],
                'email': user['email'],
                'telephone': user['telephone'],
                'role': user['role']
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================
# ENDPOINTS - DÉCONNEXION
# ============================================

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """
    POST /api/auth/logout
    Déconnexion de l'utilisateur
    """
    try:
        session.clear()
        
        return jsonify({
            'success': True,
            'message': 'Déconnexion réussie'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================
# ENDPOINTS - PROFIL
# ============================================

@auth_bp.route('/profile', methods=['GET'])
@login_required
def get_profile():
    """
    GET /api/auth/profile
    Récupère le profil de l'utilisateur connecté
    """
    try:
        user_id = session['user_id']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, nom, prenom, email, telephone, role, created_at
            FROM users
            WHERE id = ?
        ''', (user_id,))
        
        user = cursor.fetchone()
        
        if not user:
            conn.close()
            session.clear()
            return jsonify({
                'success': False,
                'error': 'Utilisateur non trouvé'
            }), 404
        
        # Compter les préinscriptions de l'utilisateur
        cursor.execute('''
            SELECT COUNT(*) FROM preinscriptions WHERE user_id = ?
        ''', (user_id,))
        
        total_preinscriptions = cursor.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'user': {
                'id': user['id'],
                'nom': user['nom'],
                'prenom': user['prenom'],
                'email': user['email'],
                'telephone': user['telephone'],
                'role': user['role'],
                'created_at': user['created_at'],
                'stats': {
                    'total_preinscriptions': total_preinscriptions
                }
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@auth_bp.route('/profile', methods=['PUT'])
@login_required
def update_profile():
    """
    PUT /api/auth/profile
    Met à jour le profil de l'utilisateur
    
    Body:
        {
            "nom": "Nouveau nom",
            "prenom": "Nouveau prénom",
            "telephone": "+237690000000"
        }
    """
    try:
        user_id = session['user_id']
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Aucune donnée fournie'
            }), 400
        
        # Champs modifiables
        updatable_fields = []
        values = []
        
        if 'nom' in data:
            updatable_fields.append('nom = ?')
            values.append(data['nom'].strip())
        
        if 'prenom' in data:
            updatable_fields.append('prenom = ?')
            values.append(data['prenom'].strip())
        
        if 'telephone' in data:
            updatable_fields.append('telephone = ?')
            values.append(data['telephone'].strip())
        
        if not updatable_fields:
            return jsonify({
                'success': False,
                'error': 'Aucun champ à mettre à jour'
            }), 400
        
        values.append(user_id)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = f"UPDATE users SET {', '.join(updatable_fields)} WHERE id = ?"
        cursor.execute(query, values)
        
        conn.commit()
        conn.close()
        
        # Mettre à jour la session
        if 'nom' in data:
            session['nom'] = data['nom'].strip()
        if 'prenom' in data:
            session['prenom'] = data['prenom'].strip()
        
        return jsonify({
            'success': True,
            'message': 'Profil mis à jour avec succès'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================
# ENDPOINTS - CHANGEMENT DE MOT DE PASSE
# ============================================

@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """
    POST /api/auth/change-password
    Change le mot de passe de l'utilisateur
    
    Body:
        {
            "current_password": "OldPassword123",
            "new_password": "NewPassword123",
            "confirm_password": "NewPassword123"
        }
    """
    try:
        user_id = session['user_id']
        data = request.get_json()
        
        required_fields = ['current_password', 'new_password', 'confirm_password']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return jsonify({
                'success': False,
                'error': f'Champs manquants: {", ".join(missing_fields)}'
            }), 400
        
        current_password = data['current_password']
        new_password = data['new_password']
        confirm_password = data['confirm_password']
        
        # Vérifier l'ancien mot de passe
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT password_hash FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        
        if not user:
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Utilisateur non trouvé'
            }), 404
        
        current_password_hash = hash_password(current_password)
        if current_password_hash != user['password_hash']:
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Mot de passe actuel incorrect'
            }), 400
        
        # Vérifier la confirmation
        if new_password != confirm_password:
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Les nouveaux mots de passe ne correspondent pas'
            }), 400
        
        # Valider le nouveau mot de passe
        is_valid, message = validate_password(new_password)
        if not is_valid:
            conn.close()
            return jsonify({
                'success': False,
                'error': message
            }), 400
        
        # Mettre à jour le mot de passe
        new_password_hash = hash_password(new_password)
        cursor.execute('''
            UPDATE users
            SET password_hash = ?
            WHERE id = ?
        ''', (new_password_hash, user_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Mot de passe changé avec succès'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================
# ENDPOINTS - VÉRIFICATION DE SESSION
# ============================================

@auth_bp.route('/check', methods=['GET'])
def check_session():
    """
    GET /api/auth/check
    Vérifie si l'utilisateur est connecté
    """
    try:
        if 'user_id' in session:
            return jsonify({
                'success': True,
                'authenticated': True,
                'user': {
                    'id': session['user_id'],
                    'email': session['email'],
                    'nom': session['nom'],
                    'prenom': session['prenom'],
                    'role': session['role']
                }
            })
        else:
            return jsonify({
                'success': True,
                'authenticated': False
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================
# ENDPOINTS - ADMIN - GESTION DES UTILISATEURS
# ============================================

@auth_bp.route('/users', methods=['GET'])
@admin_required
def get_all_users():
    """
    GET /api/auth/users
    Liste tous les utilisateurs (admin uniquement)
    
    Query Params:
        - role: filtre par rôle (admin, etudiant, visiteur)
        - page: numéro de page
        - per_page: éléments par page
    """
    try:
        role = request.args.get('role')
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = 'SELECT id, nom, prenom, email, telephone, role, created_at FROM users WHERE 1=1'
        params = []
        
        if role:
            query += ' AND role = ?'
            params.append(role)
        
        # Compter le total
        count_query = query.replace('SELECT id, nom, prenom, email, telephone, role, created_at', 'SELECT COUNT(*)')
        cursor.execute(count_query, params)
        total = cursor.fetchone()[0]
        
        # Paginer
        offset = (page - 1) * per_page
        query += f' ORDER BY created_at DESC LIMIT {per_page} OFFSET {offset}'
        
        cursor.execute(query, params)
        users = cursor.fetchall()
        conn.close()
        
        result = []
        for user in users:
            result.append({
                'id': user['id'],
                'nom': user['nom'],
                'prenom': user['prenom'],
                'email': user['email'],
                'telephone': user['telephone'],
                'role': user['role'],
                'created_at': user['created_at']
            })
        
        return jsonify({
            'success': True,
            'data': result,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'total_pages': (total + per_page - 1) // per_page
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@auth_bp.route('/users/<int:user_id>/role', methods=['PUT'])
@admin_required
def update_user_role(user_id):
    """
    PUT /api/auth/users/<id>/role
    Change le rôle d'un utilisateur (admin uniquement)
    
    Body:
        {
            "role": "admin|etudiant|visiteur"
        }
    """
    try:
        data = request.get_json()
        
        if not data or 'role' not in data:
            return jsonify({
                'success': False,
                'error': 'Rôle requis'
            }), 400
        
        role = data['role']
        valid_roles = ['admin', 'etudiant', 'visiteur']
        
        if role not in valid_roles:
            return jsonify({
                'success': False,
                'error': f'Rôle invalide. Valeurs acceptées: {", ".join(valid_roles)}'
            }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('UPDATE users SET role = ? WHERE id = ?', (role, user_id))
        
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Utilisateur non trouvé'
            }), 404
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'Rôle mis à jour: {role}'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
