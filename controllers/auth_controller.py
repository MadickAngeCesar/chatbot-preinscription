"""
Contrôleur d'authentification
Gère l'inscription, la connexion et la gestion des utilisateurs
"""

from flask import request, session, jsonify, g
from datetime import datetime
import hashlib
import sqlite3
import secrets

from middleware import (
    validate_email, 
    validate_password,
    ValidationError,
    AuthenticationError,
    log_auth_attempt,
    log_user_action
)

DATABASE = 'database/chatbot.db'

def get_db_connection():
    """Crée une connexion à la base de données"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    """Hashe un mot de passe avec SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

# ============================================
# CONTRÔLEUR - INSCRIPTION
# ============================================

def register_user():
    """
    Inscrit un nouvel utilisateur
    
    Returns:
        tuple: (response_dict, status_code)
    """
    try:
        data = request.get_json()
        
        # Extraire les données
        nom = data.get('nom', '').strip()
        prenom = data.get('prenom', '').strip()
        email = data.get('email', '').strip().lower()
        telephone = data.get('telephone', '').strip()
        password = data.get('password', '')
        role = data.get('role', 'etudiant')
        
        # Validation
        if not all([nom, prenom, email, password]):
            raise ValidationError('Tous les champs sont requis (nom, prenom, email, password)')
        
        if not validate_email(email):
            raise ValidationError('Format d\'email invalide')
        
        is_valid, message = validate_password(password)
        if not is_valid:
            raise ValidationError(message)
        
        # Vérifier que le rôle est valide
        if role not in ['admin', 'etudiant', 'visiteur']:
            role = 'etudiant'
        
        # Vérifier si l'email existe déjà
        conn = get_db_connection()
        cursor = conn.cursor()
        
        existing_user = cursor.execute(
            'SELECT id FROM users WHERE email = ?',
            (email,)
        ).fetchone()
        
        if existing_user:
            conn.close()
            log_auth_attempt(email, False, 'Email déjà enregistré')
            raise ValidationError('Cet email est déjà enregistré')
        
        # Hasher le mot de passe
        password_hash = hash_password(password)
        
        # Insérer l'utilisateur
        cursor.execute('''
            INSERT INTO users (nom, prenom, email, telephone, password_hash, role)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (nom, prenom, email, telephone, password_hash, role))
        
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Logger le succès
        log_auth_attempt(email, True)
        log_user_action('REGISTER', user_id, {'email': email, 'role': role})
        
        # Créer la session automatiquement
        session.permanent = True
        session['user_id'] = user_id
        session['email'] = email
        session['role'] = role
        session['nom'] = nom
        session['prenom'] = prenom
        session['last_activity'] = datetime.now().isoformat()
        
        return {
            'success': True,
            'message': 'Inscription réussie',
            'user': {
                'id': user_id,
                'nom': nom,
                'prenom': prenom,
                'email': email,
                'role': role
            }
        }, 201
        
    except ValidationError as e:
        return {
            'success': False,
            'error': e.message,
            'code': e.code
        }, e.status_code
    
    except sqlite3.IntegrityError as e:
        log_auth_attempt(email, False, f'Erreur d\'intégrité: {str(e)}')
        return {
            'success': False,
            'error': 'Erreur lors de l\'inscription',
            'code': 'DATABASE_ERROR'
        }, 500
    
    except Exception as e:
        print(f"❌ Erreur dans register_user: {e}")
        return {
            'success': False,
            'error': 'Erreur serveur lors de l\'inscription',
            'code': 'INTERNAL_ERROR'
        }, 500


# ============================================
# CONTRÔLEUR - CONNEXION
# ============================================

def login_user():
    """
    Connecte un utilisateur existant
    
    Returns:
        tuple: (response_dict, status_code)
    """
    try:
        data = request.get_json()
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        # Validation
        if not email or not password:
            raise ValidationError('Email et mot de passe requis')
        
        if not validate_email(email):
            raise ValidationError('Format d\'email invalide')
        
        # Rechercher l'utilisateur
        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM users WHERE email = ?',
            (email,)
        ).fetchone()
        conn.close()
        
        # Vérifier l'existence de l'utilisateur
        if not user:
            log_auth_attempt(email, False, 'Utilisateur non trouvé')
            raise AuthenticationError('Email ou mot de passe incorrect')
        
        # Vérifier le mot de passe
        password_hash = hash_password(password)
        if user['password_hash'] != password_hash:
            log_auth_attempt(email, False, 'Mot de passe incorrect')
            raise AuthenticationError('Email ou mot de passe incorrect')
        
        # Logger le succès
        log_auth_attempt(email, True)
        log_user_action('LOGIN', user['id'], {'email': email})
        
        # Créer la session
        session.permanent = True
        session['user_id'] = user['id']
        session['email'] = user['email']
        session['role'] = user['role']
        session['nom'] = user['nom']
        session['prenom'] = user['prenom']
        session['last_activity'] = datetime.now().isoformat()
        
        return {
            'success': True,
            'message': 'Connexion réussie',
            'user': {
                'id': user['id'],
                'nom': user['nom'],
                'prenom': user['prenom'],
                'email': user['email'],
                'telephone': user['telephone'],
                'role': user['role'],
                'created_at': user['created_at']
            }
        }, 200
        
    except (ValidationError, AuthenticationError) as e:
        return {
            'success': False,
            'error': e.message,
            'code': e.code
        }, e.status_code
    
    except Exception as e:
        print(f"❌ Erreur dans login_user: {e}")
        return {
            'success': False,
            'error': 'Erreur serveur lors de la connexion',
            'code': 'INTERNAL_ERROR'
        }, 500


# ============================================
# CONTRÔLEUR - DÉCONNEXION
# ============================================

def logout_user():
    """
    Déconnecte l'utilisateur courant
    
    Returns:
        tuple: (response_dict, status_code)
    """
    try:
        user_id = session.get('user_id')
        email = session.get('email')
        
        if user_id:
            log_user_action('LOGOUT', user_id, {'email': email})
        
        # Nettoyer la session
        session.clear()
        
        return {
            'success': True,
            'message': 'Déconnexion réussie'
        }, 200
        
    except Exception as e:
        print(f"❌ Erreur dans logout_user: {e}")
        return {
            'success': False,
            'error': 'Erreur lors de la déconnexion',
            'code': 'INTERNAL_ERROR'
        }, 500


# ============================================
# CONTRÔLEUR - PROFIL UTILISATEUR
# ============================================

def get_user_profile():
    """
    Récupère le profil de l'utilisateur connecté
    
    Returns:
        tuple: (response_dict, status_code)
    """
    try:
        user_id = g.user_id
        
        conn = get_db_connection()
        user = conn.execute(
            'SELECT id, nom, prenom, email, telephone, role, created_at FROM users WHERE id = ?',
            (user_id,)
        ).fetchone()
        conn.close()
        
        if not user:
            return {
                'success': False,
                'error': 'Utilisateur non trouvé',
                'code': 'NOT_FOUND'
            }, 404
        
        return {
            'success': True,
            'user': {
                'id': user['id'],
                'nom': user['nom'],
                'prenom': user['prenom'],
                'email': user['email'],
                'telephone': user['telephone'],
                'role': user['role'],
                'created_at': user['created_at']
            }
        }, 200
        
    except Exception as e:
        print(f"❌ Erreur dans get_user_profile: {e}")
        return {
            'success': False,
            'error': 'Erreur lors de la récupération du profil',
            'code': 'INTERNAL_ERROR'
        }, 500


def update_user_profile():
    """
    Met à jour le profil de l'utilisateur connecté
    
    Returns:
        tuple: (response_dict, status_code)
    """
    try:
        user_id = g.user_id
        data = request.get_json()
        
        # Champs autorisés à la mise à jour
        allowed_fields = ['nom', 'prenom', 'telephone']
        updates = {}
        
        for field in allowed_fields:
            if field in data:
                updates[field] = data[field].strip() if isinstance(data[field], str) else data[field]
        
        if not updates:
            raise ValidationError('Aucun champ à mettre à jour')
        
        # Construire la requête SQL
        set_clause = ', '.join([f"{field} = ?" for field in updates.keys()])
        values = list(updates.values()) + [user_id]
        
        conn = get_db_connection()
        conn.execute(
            f'UPDATE users SET {set_clause} WHERE id = ?',
            values
        )
        conn.commit()
        
        # Récupérer l'utilisateur mis à jour
        user = conn.execute(
            'SELECT id, nom, prenom, email, telephone, role, created_at FROM users WHERE id = ?',
            (user_id,)
        ).fetchone()
        conn.close()
        
        # Mettre à jour la session
        if 'nom' in updates:
            session['nom'] = updates['nom']
        if 'prenom' in updates:
            session['prenom'] = updates['prenom']
        
        log_user_action('UPDATE_PROFILE', user_id, updates)
        
        return {
            'success': True,
            'message': 'Profil mis à jour avec succès',
            'user': {
                'id': user['id'],
                'nom': user['nom'],
                'prenom': user['prenom'],
                'email': user['email'],
                'telephone': user['telephone'],
                'role': user['role'],
                'created_at': user['created_at']
            }
        }, 200
        
    except ValidationError as e:
        return {
            'success': False,
            'error': e.message,
            'code': e.code
        }, e.status_code
    
    except Exception as e:
        print(f"❌ Erreur dans update_user_profile: {e}")
        return {
            'success': False,
            'error': 'Erreur lors de la mise à jour du profil',
            'code': 'INTERNAL_ERROR'
        }, 500


# ============================================
# CONTRÔLEUR - CHANGEMENT DE MOT DE PASSE
# ============================================

def change_password():
    """
    Change le mot de passe de l'utilisateur connecté
    
    Returns:
        tuple: (response_dict, status_code)
    """
    try:
        user_id = g.user_id
        data = request.get_json()
        
        current_password = data.get('current_password', '')
        new_password = data.get('new_password', '')
        
        if not current_password or not new_password:
            raise ValidationError('Mot de passe actuel et nouveau mot de passe requis')
        
        # Valider le nouveau mot de passe
        is_valid, message = validate_password(new_password)
        if not is_valid:
            raise ValidationError(message)
        
        # Vérifier le mot de passe actuel
        conn = get_db_connection()
        user = conn.execute(
            'SELECT password_hash FROM users WHERE id = ?',
            (user_id,)
        ).fetchone()
        
        if not user:
            conn.close()
            return {
                'success': False,
                'error': 'Utilisateur non trouvé',
                'code': 'NOT_FOUND'
            }, 404
        
        current_password_hash = hash_password(current_password)
        if user['password_hash'] != current_password_hash:
            conn.close()
            raise AuthenticationError('Mot de passe actuel incorrect')
        
        # Mettre à jour le mot de passe
        new_password_hash = hash_password(new_password)
        conn.execute(
            'UPDATE users SET password_hash = ? WHERE id = ?',
            (new_password_hash, user_id)
        )
        conn.commit()
        conn.close()
        
        log_user_action('CHANGE_PASSWORD', user_id)
        
        return {
            'success': True,
            'message': 'Mot de passe changé avec succès'
        }, 200
        
    except (ValidationError, AuthenticationError) as e:
        return {
            'success': False,
            'error': e.message,
            'code': e.code
        }, e.status_code
    
    except Exception as e:
        print(f"❌ Erreur dans change_password: {e}")
        return {
            'success': False,
            'error': 'Erreur lors du changement de mot de passe',
            'code': 'INTERNAL_ERROR'
        }, 500
