"""
Contrôleur d'établissements
Gère les établissements universitaires
"""

from flask import request, g
import sqlite3

from middleware import ValidationError

DATABASE = 'database/chatbot.db'

def get_db_connection():
    """Crée une connexion à la base de données"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# ============================================
# CONTRÔLEUR - LISTE DES ÉTABLISSEMENTS
# ============================================

def get_etablissements():
    """
    Récupère la liste de tous les établissements
    
    Returns:
        tuple: (response_dict, status_code)
    """
    try:
        # Paramètres de requête
        actif = request.args.get('actif', 1, type=int)
        type_etab = request.args.get('type')
        ville = request.args.get('ville')
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        offset = (page - 1) * per_page
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Construction de la requête
        query = '''
            SELECT id, nom, code, adresse, ville, telephone, email, site_web, type, actif
            FROM etablissements
            WHERE actif = ?
        '''
        params = [actif]
        
        if type_etab:
            query += ' AND type = ?'
            params.append(type_etab)
        
        if ville:
            query += ' AND ville LIKE ?'
            params.append(f'%{ville}%')
        
        query += ' ORDER BY nom LIMIT ? OFFSET ?'
        params.extend([per_page, offset])
        
        etablissements = cursor.execute(query, params).fetchall()
        
        # Compter le total
        count_query = 'SELECT COUNT(*) FROM etablissements WHERE actif = ?'
        count_params = [actif]
        
        if type_etab:
            count_query += ' AND type = ?'
            count_params.append(type_etab)
        
        if ville:
            count_query += ' AND ville LIKE ?'
            count_params.append(f'%{ville}%')
        
        total = cursor.execute(count_query, count_params).fetchone()[0]
        conn.close()
        
        result = []
        for etab in etablissements:
            result.append({
                'id': etab['id'],
                'nom': etab['nom'],
                'code': etab['code'],
                'adresse': etab['adresse'],
                'ville': etab['ville'],
                'telephone': etab['telephone'],
                'email': etab['email'],
                'site_web': etab['site_web'],
                'type': etab['type'],
                'actif': etab['actif']
            })
        
        return {
            'success': True,
            'data': result,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        }, 200
        
    except Exception as e:
        print(f"❌ Erreur dans get_etablissements: {e}")
        return {
            'success': False,
            'error': 'Erreur lors de la récupération des établissements',
            'code': 'INTERNAL_ERROR'
        }, 500


# ============================================
# CONTRÔLEUR - DÉTAILS D'UN ÉTABLISSEMENT
# ============================================

def get_etablissement_detail(etablissement_id):
    """
    Récupère les détails d'un établissement spécifique
    
    Args:
        etablissement_id: ID de l'établissement
        
    Returns:
        tuple: (response_dict, status_code)
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        etablissement = cursor.execute('''
            SELECT * FROM etablissements WHERE id = ?
        ''', (etablissement_id,)).fetchone()
        
        if not etablissement:
            conn.close()
            return {
                'success': False,
                'error': 'Établissement non trouvé',
                'code': 'NOT_FOUND'
            }, 404
        
        # Récupérer les filières associées
        filieres = cursor.execute('''
            SELECT id, nom, code, niveau, places_disponibles
            FROM filieres
            WHERE etablissement_id = ? AND actif = 1
            ORDER BY niveau, nom
        ''', (etablissement_id,)).fetchall()
        
        conn.close()
        
        result = {
            'id': etablissement['id'],
            'nom': etablissement['nom'],
            'code': etablissement['code'],
            'adresse': etablissement['adresse'],
            'ville': etablissement['ville'],
            'telephone': etablissement['telephone'],
            'email': etablissement['email'],
            'site_web': etablissement['site_web'],
            'type': etablissement['type'],
            'actif': etablissement['actif'],
            'date_creation': etablissement['date_creation'],
            'filieres': [
                {
                    'id': f['id'],
                    'nom': f['nom'],
                    'code': f['code'],
                    'niveau': f['niveau'],
                    'places_disponibles': f['places_disponibles']
                }
                for f in filieres
            ]
        }
        
        return {
            'success': True,
            'data': result
        }, 200
        
    except Exception as e:
        print(f"❌ Erreur dans get_etablissement_detail: {e}")
        return {
            'success': False,
            'error': 'Erreur lors de la récupération des détails',
            'code': 'INTERNAL_ERROR'
        }, 500


# ============================================
# CONTRÔLEUR - STATISTIQUES D'UN ÉTABLISSEMENT
# ============================================

def get_etablissement_stats(etablissement_id):
    """
    Récupère les statistiques d'un établissement
    
    Args:
        etablissement_id: ID de l'établissement
        
    Returns:
        tuple: (response_dict, status_code)
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Vérifier que l'établissement existe
        etablissement = cursor.execute(
            'SELECT nom FROM etablissements WHERE id = ?',
            (etablissement_id,)
        ).fetchone()
        
        if not etablissement:
            conn.close()
            return {
                'success': False,
                'error': 'Établissement non trouvé',
                'code': 'NOT_FOUND'
            }, 404
        
        # Nombre de filières
        nb_filieres = cursor.execute(
            'SELECT COUNT(*) FROM filieres WHERE etablissement_id = ? AND actif = 1',
            (etablissement_id,)
        ).fetchone()[0]
        
        # Nombre de préinscriptions par statut
        preinscriptions_stats = cursor.execute('''
            SELECT 
                statut,
                COUNT(*) as count
            FROM preinscriptions
            WHERE etablissement_id = ?
            GROUP BY statut
        ''', (etablissement_id,)).fetchall()
        
        # Total des préinscriptions
        total_preinscriptions = cursor.execute(
            'SELECT COUNT(*) FROM preinscriptions WHERE etablissement_id = ?',
            (etablissement_id,)
        ).fetchone()[0]
        
        conn.close()
        
        result = {
            'etablissement': {
                'id': etablissement_id,
                'nom': etablissement['nom']
            },
            'statistiques': {
                'nb_filieres': nb_filieres,
                'total_preinscriptions': total_preinscriptions,
                'preinscriptions_par_statut': {
                    row['statut']: row['count']
                    for row in preinscriptions_stats
                }
            }
        }
        
        return {
            'success': True,
            'data': result
        }, 200
        
    except Exception as e:
        print(f"❌ Erreur dans get_etablissement_stats: {e}")
        return {
            'success': False,
            'error': 'Erreur lors de la récupération des statistiques',
            'code': 'INTERNAL_ERROR'
        }, 500
