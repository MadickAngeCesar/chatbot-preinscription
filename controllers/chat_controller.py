"""
Contrôleur de chat
Gère les conversations avec le chatbot
"""

from flask import request, session, g
from datetime import datetime
import sqlite3
import secrets

from services import gemini_chatbot
from middleware import log_user_action

DATABASE = 'database/chatbot.db'

def get_db_connection():
    """Crée une connexion à la base de données"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# ============================================
# CONTRÔLEUR - ENVOI DE MESSAGE
# ============================================

def send_message():
    """
    Envoie un message au chatbot et récupère la réponse
    
    Returns:
        tuple: (response_dict, status_code)
    """
    try:
        data = request.get_json()
        
        message = data.get('message', '').strip()
        session_id = data.get('session_id') or session.get('chat_session_id')
        
        if not message:
            return {
                'success': False,
                'error': 'Le message ne peut pas être vide',
                'code': 'EMPTY_MESSAGE'
            }, 400
        
        # Créer une session de chat si nécessaire
        if not session_id:
            session_id = secrets.token_hex(16)
            session['chat_session_id'] = session_id
            
            # Enregistrer la session dans la BD
            conn = get_db_connection()
            user_id = g.user_id if hasattr(g, 'user_id') else None
            conn.execute(
                'INSERT INTO chat_sessions (session_id, user_id) VALUES (?, ?)',
                (session_id, user_id)
            )
            conn.commit()
            conn.close()
        
        # Sauvegarder le message de l'utilisateur
        conn = get_db_connection()
        user_id = g.user_id if hasattr(g, 'user_id') else None
        
        conn.execute(
            'INSERT INTO messages (session_id, user_id, role, contenu) VALUES (?, ?, ?, ?)',
            (session_id, user_id, 'user', message)
        )
        conn.commit()
        
        # Récupérer le nom de l'utilisateur si connecté
        user_name = None
        if user_id:
            try:
                user = conn.execute(
                    'SELECT nom, prenom FROM users WHERE id = ?',
                    (user_id,)
                ).fetchone()
                if user:
                    user_name = f"{user['prenom']} {user['nom']}"
            except:
                pass
        
        # Générer la réponse avec Gemini AI
        try:
            bot_response = gemini_chatbot.generate_response(message, session_id, user_name)
        except Exception as e:
            print(f"⚠️ Erreur Gemini, utilisation fallback: {e}")
            bot_response = gemini_chatbot.get_fallback_response(message)
        
        # Sauvegarder la réponse du bot
        conn.execute(
            'INSERT INTO messages (session_id, user_id, role, contenu) VALUES (?, ?, ?, ?)',
            (session_id, user_id, 'bot', bot_response)
        )
        conn.commit()
        
        # Mettre à jour l'activité de la session
        conn.execute(
            'UPDATE chat_sessions SET last_activity = CURRENT_TIMESTAMP WHERE session_id = ?',
            (session_id,)
        )
        conn.commit()
        conn.close()
        
        if user_id:
            log_user_action('CHAT_MESSAGE', user_id, {
                'session_id': session_id,
                'message_length': len(message)
            })
        
        return {
            'success': True,
            'response': bot_response,
            'session_id': session_id,
            'timestamp': datetime.now().isoformat()
        }, 200
        
    except Exception as e:
        print(f"❌ Erreur dans send_message: {e}")
        return {
            'success': False,
            'error': 'Erreur lors de l\'envoi du message',
            'code': 'INTERNAL_ERROR'
        }, 500


# ============================================
# CONTRÔLEUR - HISTORIQUE DES MESSAGES
# ============================================

def get_message_history(session_id):
    """
    Récupère l'historique des messages d'une session
    
    Args:
        session_id: ID de la session de chat
        
    Returns:
        tuple: (response_dict, status_code)
    """
    try:
        conn = get_db_connection()
        
        # Vérifier que la session existe
        session_row = conn.execute(
            'SELECT id FROM chat_sessions WHERE session_id = ?',
            (session_id,)
        ).fetchone()
        
        if not session_row:
            conn.close()
            return {
                'success': False,
                'error': 'Session de chat non trouvée',
                'code': 'SESSION_NOT_FOUND'
            }, 404
        
        # Récupérer les messages
        messages = conn.execute('''
            SELECT role, contenu, timestamp
            FROM messages
            WHERE session_id = ?
            ORDER BY timestamp ASC
        ''', (session_id,)).fetchall()
        conn.close()
        
        result = []
        for msg in messages:
            result.append({
                'role': msg['role'],
                'content': msg['contenu'],
                'timestamp': msg['timestamp']
            })
        
        return {
            'success': True,
            'session_id': session_id,
            'messages': result,
            'count': len(result)
        }, 200
        
    except Exception as e:
        print(f"❌ Erreur dans get_message_history: {e}")
        return {
            'success': False,
            'error': 'Erreur lors de la récupération de l\'historique',
            'code': 'INTERNAL_ERROR'
        }, 500


# ============================================
# CONTRÔLEUR - SESSIONS DE CHAT
# ============================================

def get_user_chat_sessions():
    """
    Récupère toutes les sessions de chat de l'utilisateur connecté
    
    Returns:
        tuple: (response_dict, status_code)
    """
    try:
        user_id = g.user_id
        
        conn = get_db_connection()
        sessions = conn.execute('''
            SELECT 
                cs.session_id,
                cs.created_at,
                cs.last_activity,
                COUNT(m.id) as message_count
            FROM chat_sessions cs
            LEFT JOIN messages m ON cs.session_id = m.session_id
            WHERE cs.user_id = ?
            GROUP BY cs.session_id
            ORDER BY cs.last_activity DESC
        ''', (user_id,)).fetchall()
        conn.close()
        
        result = []
        for s in sessions:
            result.append({
                'session_id': s['session_id'],
                'created_at': s['created_at'],
                'last_activity': s['last_activity'],
                'message_count': s['message_count']
            })
        
        return {
            'success': True,
            'sessions': result,
            'count': len(result)
        }, 200
        
    except Exception as e:
        print(f"❌ Erreur dans get_user_chat_sessions: {e}")
        return {
            'success': False,
            'error': 'Erreur lors de la récupération des sessions',
            'code': 'INTERNAL_ERROR'
        }, 500


def delete_chat_session(session_id):
    """
    Supprime une session de chat et tous ses messages
    
    Args:
        session_id: ID de la session à supprimer
        
    Returns:
        tuple: (response_dict, status_code)
    """
    try:
        user_id = g.user_id
        
        conn = get_db_connection()
        
        # Vérifier que la session appartient à l'utilisateur
        session_row = conn.execute(
            'SELECT user_id FROM chat_sessions WHERE session_id = ?',
            (session_id,)
        ).fetchone()
        
        if not session_row:
            conn.close()
            return {
                'success': False,
                'error': 'Session non trouvée',
                'code': 'SESSION_NOT_FOUND'
            }, 404
        
        if session_row['user_id'] != user_id:
            conn.close()
            return {
                'success': False,
                'error': 'Vous ne pouvez supprimer que vos propres sessions',
                'code': 'FORBIDDEN'
            }, 403
        
        # Supprimer la session (les messages seront supprimés en cascade)
        conn.execute(
            'DELETE FROM chat_sessions WHERE session_id = ?',
            (session_id,)
        )
        conn.commit()
        conn.close()
        
        log_user_action('DELETE_CHAT_SESSION', user_id, {'session_id': session_id})
        
        return {
            'success': True,
            'message': 'Session supprimée avec succès'
        }, 200
        
    except Exception as e:
        print(f"❌ Erreur dans delete_chat_session: {e}")
        return {
            'success': False,
            'error': 'Erreur lors de la suppression de la session',
            'code': 'INTERNAL_ERROR'
        }, 500
