"""
API REST - Chatbot de Préinscription Universitaire
Documentation complète des endpoints
Auteur: Madick Ange César
Date: Novembre 2025
"""

from flask import Blueprint, request, jsonify
from functools import wraps
import sqlite3
from datetime import datetime
import os

# Créer le Blueprint pour l'API
api_bp = Blueprint('api', __name__, url_prefix='/api')

# ============================================
# CONFIGURATION
# ============================================

DATABASE = 'database/chatbot.db'

def get_db_connection():
    """Crée une connexion à la base de données"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# ============================================
# DÉCORATEURS ET UTILITAIRES
# ============================================

def validate_json(*required_fields):
    """Décorateur pour valider les champs JSON requis"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return jsonify({
                    'success': False,
                    'error': 'Content-Type doit être application/json'
                }), 400
            
            data = request.get_json()
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                return jsonify({
                    'success': False,
                    'error': f'Champs requis manquants: {", ".join(missing_fields)}'
                }), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def paginate(query, page=1, per_page=10):
    """Utilitaire pour paginer les résultats"""
    offset = (page - 1) * per_page
    return f"{query} LIMIT {per_page} OFFSET {offset}"

# ============================================
# ENDPOINTS - ÉTABLISSEMENTS
# ============================================

@api_bp.route('/etablissements', methods=['GET'])
def get_etablissements():
    """
    GET /api/etablissements
    Récupère la liste de tous les établissements
    
    Query Params:
        - actif: (0|1) filtre par statut actif (défaut: 1)
        - type: filtre par type (université, école, institut)
        - ville: filtre par ville
        - page: numéro de page (défaut: 1)
        - per_page: nombre d'éléments par page (défaut: 20)
    
    Response:
        {
            "success": true,
            "data": [...],
            "pagination": {
                "page": 1,
                "per_page": 20,
                "total": 42
            }
        }
    """
    try:
        # Récupérer les paramètres de requête
        actif = request.args.get('actif', 1, type=int)
        type_etab = request.args.get('type')
        ville = request.args.get('ville')
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Construire la requête avec filtres
        query = 'SELECT * FROM etablissements WHERE actif = ?'
        params = [actif]
        
        if type_etab:
            query += ' AND type = ?'
            params.append(type_etab)
        
        if ville:
            query += ' AND ville LIKE ?'
            params.append(f'%{ville}%')
        
        # Compter le total
        count_query = query.replace('SELECT *', 'SELECT COUNT(*)')
        cursor.execute(count_query, params)
        total = cursor.fetchone()[0]
        
        # Ajouter l'ordre et la pagination
        query += ' ORDER BY nom'
        query = paginate(query, page, per_page)
        
        cursor.execute(query, params)
        etablissements = cursor.fetchall()
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
                'actif': bool(etab['actif']),
                'date_creation': etab['date_creation']
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

@api_bp.route('/etablissements/<int:etablissement_id>', methods=['GET'])
def get_etablissement_detail(etablissement_id):
    """
    GET /api/etablissements/<id>
    Récupère les détails d'un établissement
    
    Response:
        {
            "success": true,
            "data": {...},
            "stats": {
                "total_filieres": 12,
                "total_preinscriptions": 245
            }
        }
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Récupérer l'établissement
        cursor.execute('SELECT * FROM etablissements WHERE id = ?', (etablissement_id,))
        etab = cursor.fetchone()
        
        if not etab:
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Établissement non trouvé'
            }), 404
        
        # Récupérer les statistiques
        cursor.execute('SELECT COUNT(*) FROM filieres WHERE etablissement_id = ?', (etablissement_id,))
        total_filieres = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM preinscriptions WHERE etablissement_id = ?', (etablissement_id,))
        total_preinscriptions = cursor.fetchone()[0]
        
        conn.close()
        
        result = {
            'id': etab['id'],
            'nom': etab['nom'],
            'code': etab['code'],
            'adresse': etab['adresse'],
            'ville': etab['ville'],
            'telephone': etab['telephone'],
            'email': etab['email'],
            'site_web': etab['site_web'],
            'type': etab['type'],
            'actif': bool(etab['actif']),
            'date_creation': etab['date_creation']
        }
        
        return jsonify({
            'success': True,
            'data': result,
            'stats': {
                'total_filieres': total_filieres,
                'total_preinscriptions': total_preinscriptions
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================
# ENDPOINTS - FILIÈRES
# ============================================

@api_bp.route('/filieres', methods=['GET'])
def get_filieres():
    """
    GET /api/filieres
    Récupère la liste des filières
    
    Query Params:
        - etablissement_id: filtre par établissement
        - niveau: filtre par niveau (Licence, Master, Doctorat)
        - departement: filtre par département
        - actif: (0|1) filtre par statut actif (défaut: 1)
        - disponible: (0|1) filtre par places disponibles > 0
        - page: numéro de page (défaut: 1)
        - per_page: nombre d'éléments par page (défaut: 20)
    
    Response:
        {
            "success": true,
            "data": [...],
            "pagination": {...}
        }
    """
    try:
        # Récupérer les paramètres
        etablissement_id = request.args.get('etablissement_id', type=int)
        niveau = request.args.get('niveau')
        departement = request.args.get('departement')
        actif = request.args.get('actif', 1, type=int)
        disponible = request.args.get('disponible', type=int)
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Construire la requête
        query = '''
            SELECT f.*, e.nom as etablissement_nom, e.code as etablissement_code,
                   e.ville as etablissement_ville
            FROM filieres f
            JOIN etablissements e ON f.etablissement_id = e.id
            WHERE f.actif = ?
        '''
        params = [actif]
        
        if etablissement_id:
            query += ' AND f.etablissement_id = ?'
            params.append(etablissement_id)
        
        if niveau:
            query += ' AND f.niveau = ?'
            params.append(niveau)
        
        if departement:
            query += ' AND f.departement LIKE ?'
            params.append(f'%{departement}%')
        
        if disponible is not None:
            if disponible == 1:
                query += ' AND f.places_disponibles > 0'
            else:
                query += ' AND f.places_disponibles = 0'
        
        # Compter le total
        count_query = query.replace('SELECT f.*, e.nom as etablissement_nom, e.code as etablissement_code, e.ville as etablissement_ville', 'SELECT COUNT(*)')
        cursor.execute(count_query, params)
        total = cursor.fetchone()[0]
        
        # Ajouter l'ordre et la pagination
        query += ' ORDER BY f.niveau, f.nom'
        query = paginate(query, page, per_page)
        
        cursor.execute(query, params)
        filieres = cursor.fetchall()
        conn.close()
        
        result = []
        for fil in filieres:
            result.append({
                'id': fil['id'],
                'nom': fil['nom'],
                'code': fil['code'],
                'niveau': fil['niveau'],
                'departement': fil['departement'],
                'duree': fil['duree'],
                'frais_inscription': fil['frais_inscription'],
                'frais_scolarite': fil['frais_scolarite'],
                'places_disponibles': fil['places_disponibles'],
                'description': fil['description'],
                'prerequis': fil['prerequis'],
                'actif': bool(fil['actif']),
                'etablissement': {
                    'id': fil['etablissement_id'],
                    'nom': fil['etablissement_nom'],
                    'code': fil['etablissement_code'],
                    'ville': fil['etablissement_ville']
                }
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

@api_bp.route('/filieres/<int:filiere_id>', methods=['GET'])
def get_filiere_detail(filiere_id):
    """
    GET /api/filieres/<id>
    Récupère les détails complets d'une filière
    
    Response:
        {
            "success": true,
            "data": {...},
            "stats": {
                "total_preinscriptions": 45,
                "taux_occupation": 75.0
            }
        }
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT f.*, e.nom as etablissement_nom, e.code as etablissement_code,
                   e.ville, e.telephone, e.email, e.adresse, e.site_web
            FROM filieres f
            JOIN etablissements e ON f.etablissement_id = e.id
            WHERE f.id = ?
        ''', (filiere_id,))
        
        filiere = cursor.fetchone()
        
        if not filiere:
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Filière non trouvée'
            }), 404
        
        # Récupérer les statistiques
        cursor.execute('SELECT COUNT(*) FROM preinscriptions WHERE filiere_id = ?', (filiere_id,))
        total_preinscriptions = cursor.fetchone()[0]
        
        conn.close()
        
        # Calculer le taux d'occupation
        places_totales = filiere['places_disponibles'] + total_preinscriptions
        taux_occupation = (total_preinscriptions / places_totales * 100) if places_totales > 0 else 0
        
        result = {
            'id': filiere['id'],
            'nom': filiere['nom'],
            'code': filiere['code'],
            'niveau': filiere['niveau'],
            'departement': filiere['departement'],
            'duree': filiere['duree'],
            'frais_inscription': filiere['frais_inscription'],
            'frais_scolarite': filiere['frais_scolarite'],
            'places_disponibles': filiere['places_disponibles'],
            'description': filiere['description'],
            'prerequis': filiere['prerequis'],
            'actif': bool(filiere['actif']),
            'date_ouverture': filiere['date_ouverture'],
            'date_fermeture': filiere['date_fermeture'],
            'etablissement': {
                'id': filiere['etablissement_id'],
                'nom': filiere['etablissement_nom'],
                'code': filiere['etablissement_code'],
                'ville': filiere['ville'],
                'telephone': filiere['telephone'],
                'email': filiere['email'],
                'adresse': filiere['adresse'],
                'site_web': filiere['site_web']
            }
        }
        
        return jsonify({
            'success': True,
            'data': result,
            'stats': {
                'total_preinscriptions': total_preinscriptions,
                'taux_occupation': round(taux_occupation, 2),
                'places_restantes': filiere['places_disponibles']
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================
# ENDPOINTS - PRÉINSCRIPTIONS
# ============================================

@api_bp.route('/preinscriptions', methods=['GET'])
def get_preinscriptions():
    """
    GET /api/preinscriptions
    Récupère la liste des préinscriptions
    
    Query Params:
        - etablissement_id: filtre par établissement
        - filiere_id: filtre par filière
        - statut: filtre par statut (nouveau, en_cours, validé, rejeté)
        - email: recherche par email
        - page: numéro de page (défaut: 1)
        - per_page: nombre d'éléments par page (défaut: 20)
    
    Response:
        {
            "success": true,
            "data": [...],
            "pagination": {...},
            "stats": {
                "total": 245,
                "nouveau": 45,
                "en_cours": 120,
                "validé": 70,
                "rejeté": 10
            }
        }
    """
    try:
        # Récupérer les paramètres
        etablissement_id = request.args.get('etablissement_id', type=int)
        filiere_id = request.args.get('filiere_id', type=int)
        statut = request.args.get('statut')
        email = request.args.get('email')
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Construire la requête
        query = '''
            SELECT p.*, 
                   e.nom as etablissement_nom, e.code as etablissement_code,
                   f.nom as filiere_nom, f.code as filiere_code, f.niveau
            FROM preinscriptions p
            JOIN etablissements e ON p.etablissement_id = e.id
            JOIN filieres f ON p.filiere_id = f.id
            WHERE 1=1
        '''
        params = []
        
        if etablissement_id:
            query += ' AND p.etablissement_id = ?'
            params.append(etablissement_id)
        
        if filiere_id:
            query += ' AND p.filiere_id = ?'
            params.append(filiere_id)
        
        if statut:
            query += ' AND p.statut = ?'
            params.append(statut)
        
        if email:
            query += ' AND p.email LIKE ?'
            params.append(f'%{email}%')
        
        # Compter le total
        count_query = query.replace('SELECT p.*, e.nom as etablissement_nom, e.code as etablissement_code, f.nom as filiere_nom, f.code as filiere_code, f.niveau', 'SELECT COUNT(*)')
        cursor.execute(count_query, params)
        total = cursor.fetchone()[0]
        
        # Statistiques par statut
        cursor.execute('SELECT statut, COUNT(*) FROM preinscriptions GROUP BY statut')
        stats_statut = dict(cursor.fetchall())
        
        # Ajouter l'ordre et la pagination
        query += ' ORDER BY p.date_soumission DESC'
        query = paginate(query, page, per_page)
        
        cursor.execute(query, params)
        preinscriptions = cursor.fetchall()
        conn.close()
        
        result = []
        for p in preinscriptions:
            result.append({
                'id': p['id'],
                'nom': p['nom'],
                'prenom': p['prenom'],
                'email': p['email'],
                'telephone': p['telephone'],
                'date_naissance': p['date_naissance'],
                'lieu_naissance': p['lieu_naissance'],
                'adresse': p['adresse'],
                'niveau': p['niveau'],
                'motivation': p['motivation'],
                'statut': p['statut'],
                'date_soumission': p['date_soumission'],
                'etablissement': {
                    'id': p['etablissement_id'],
                    'nom': p['etablissement_nom'],
                    'code': p['etablissement_code']
                },
                'filiere': {
                    'id': p['filiere_id'],
                    'nom': p['filiere_nom'],
                    'code': p['filiere_code'],
                    'niveau': p['niveau']
                }
            })
        
        return jsonify({
            'success': True,
            'data': result,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'total_pages': (total + per_page - 1) // per_page
            },
            'stats': {
                'total': total,
                'nouveau': stats_statut.get('nouveau', 0),
                'en_cours': stats_statut.get('en_cours', 0),
                'validé': stats_statut.get('validé', 0),
                'rejeté': stats_statut.get('rejeté', 0)
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/preinscriptions/<int:preinscription_id>', methods=['GET'])
def get_preinscription_detail(preinscription_id):
    """
    GET /api/preinscriptions/<id>
    Récupère les détails complets d'une préinscription
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT p.*, 
                   e.nom as etablissement_nom, e.code as etablissement_code,
                   e.ville as etablissement_ville, e.telephone as etablissement_telephone,
                   f.nom as filiere_nom, f.code as filiere_code, f.niveau,
                   f.frais_inscription, f.frais_scolarite
            FROM preinscriptions p
            JOIN etablissements e ON p.etablissement_id = e.id
            JOIN filieres f ON p.filiere_id = f.id
            WHERE p.id = ?
        ''', (preinscription_id,))
        
        p = cursor.fetchone()
        conn.close()
        
        if not p:
            return jsonify({
                'success': False,
                'error': 'Préinscription non trouvée'
            }), 404
        
        result = {
            'id': p['id'],
            'nom': p['nom'],
            'prenom': p['prenom'],
            'email': p['email'],
            'telephone': p['telephone'],
            'date_naissance': p['date_naissance'],
            'lieu_naissance': p['lieu_naissance'],
            'adresse': p['adresse'],
            'niveau': p['niveau'],
            'motivation': p['motivation'],
            'statut': p['statut'],
            'accept_terms': bool(p['accept_terms']),
            'newsletter': bool(p['newsletter']),
            'date_soumission': p['date_soumission'],
            'documents': {
                'photo': p['photo_path'],
                'diplome': p['diplome_path'],
                'releve': p['releve_path'],
                'cv': p['cv_path']
            },
            'etablissement': {
                'id': p['etablissement_id'],
                'nom': p['etablissement_nom'],
                'code': p['etablissement_code'],
                'ville': p['etablissement_ville'],
                'telephone': p['etablissement_telephone']
            },
            'filiere': {
                'id': p['filiere_id'],
                'nom': p['filiere_nom'],
                'code': p['filiere_code'],
                'niveau': p['niveau'],
                'frais_inscription': p['frais_inscription'],
                'frais_scolarite': p['frais_scolarite']
            }
        }
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/preinscriptions/<int:preinscription_id>/statut', methods=['PUT'])
@validate_json('statut')
def update_preinscription_statut(preinscription_id):
    """
    PUT /api/preinscriptions/<id>/statut
    Met à jour le statut d'une préinscription
    
    Body:
        {
            "statut": "validé|rejeté|en_cours"
        }
    """
    try:
        data = request.get_json()
        statut = data.get('statut')
        
        # Valider le statut
        statuts_valides = ['nouveau', 'en_cours', 'validé', 'rejeté']
        if statut not in statuts_valides:
            return jsonify({
                'success': False,
                'error': f'Statut invalide. Valeurs acceptées: {", ".join(statuts_valides)}'
            }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE preinscriptions
            SET statut = ?
            WHERE id = ?
        ''', (statut, preinscription_id))
        
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Préinscription non trouvée'
            }), 404
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'Statut mis à jour: {statut}'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================
# ENDPOINTS - STATISTIQUES
# ============================================

@api_bp.route('/stats/dashboard', methods=['GET'])
def get_dashboard_stats():
    """
    GET /api/stats/dashboard
    Récupère les statistiques globales pour le tableau de bord
    
    Response:
        {
            "success": true,
            "data": {
                "etablissements": {...},
                "filieres": {...},
                "preinscriptions": {...},
                "evolution": [...]
            }
        }
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Statistiques établissements
        cursor.execute('SELECT COUNT(*) FROM etablissements WHERE actif = 1')
        total_etablissements = cursor.fetchone()[0]
        
        # Statistiques filières
        cursor.execute('SELECT COUNT(*) FROM filieres WHERE actif = 1')
        total_filieres = cursor.fetchone()[0]
        
        cursor.execute('SELECT niveau, COUNT(*) FROM filieres WHERE actif = 1 GROUP BY niveau')
        filieres_par_niveau = dict(cursor.fetchall())
        
        # Statistiques préinscriptions
        cursor.execute('SELECT COUNT(*) FROM preinscriptions')
        total_preinscriptions = cursor.fetchone()[0]
        
        cursor.execute('SELECT statut, COUNT(*) FROM preinscriptions GROUP BY statut')
        preinscriptions_par_statut = dict(cursor.fetchall())
        
        # Évolution des préinscriptions (derniers 7 jours)
        cursor.execute('''
            SELECT DATE(date_soumission) as date, COUNT(*) as count
            FROM preinscriptions
            WHERE date_soumission >= date('now', '-7 days')
            GROUP BY DATE(date_soumission)
            ORDER BY date
        ''')
        evolution = [{'date': row['date'], 'count': row['count']} for row in cursor.fetchall()]
        
        # Top filières
        cursor.execute('''
            SELECT f.nom, f.niveau, COUNT(p.id) as inscriptions
            FROM filieres f
            LEFT JOIN preinscriptions p ON f.id = p.filiere_id
            WHERE f.actif = 1
            GROUP BY f.id
            ORDER BY inscriptions DESC
            LIMIT 5
        ''')
        top_filieres = [{'nom': row['nom'], 'niveau': row['niveau'], 'inscriptions': row['inscriptions']} 
                        for row in cursor.fetchall()]
        
        conn.close()
        
        result = {
            'etablissements': {
                'total': total_etablissements
            },
            'filieres': {
                'total': total_filieres,
                'par_niveau': filieres_par_niveau
            },
            'preinscriptions': {
                'total': total_preinscriptions,
                'par_statut': preinscriptions_par_statut
            },
            'evolution': evolution,
            'top_filieres': top_filieres
        }
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================
# ENDPOINTS - RECHERCHE
# ============================================

@api_bp.route('/search', methods=['GET'])
def search():
    """
    GET /api/search
    Recherche globale dans les établissements et filières
    
    Query Params:
        - q: terme de recherche (requis)
        - type: type de recherche (etablissements, filieres, all) défaut: all
    
    Response:
        {
            "success": true,
            "data": {
                "etablissements": [...],
                "filieres": [...]
            }
        }
    """
    try:
        query = request.args.get('q', '').strip()
        search_type = request.args.get('type', 'all')
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Le paramètre "q" est requis'
            }), 400
        
        if len(query) < 2:
            return jsonify({
                'success': False,
                'error': 'La recherche doit contenir au moins 2 caractères'
            }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        result = {}
        search_pattern = f'%{query}%'
        
        # Recherche dans les établissements
        if search_type in ['all', 'etablissements']:
            cursor.execute('''
                SELECT id, nom, code, ville, type
                FROM etablissements
                WHERE actif = 1 
                  AND (nom LIKE ? OR code LIKE ? OR ville LIKE ?)
                LIMIT 10
            ''', (search_pattern, search_pattern, search_pattern))
            
            result['etablissements'] = [dict(row) for row in cursor.fetchall()]
        
        # Recherche dans les filières
        if search_type in ['all', 'filieres']:
            cursor.execute('''
                SELECT f.id, f.nom, f.code, f.niveau, f.departement,
                       e.nom as etablissement_nom
                FROM filieres f
                JOIN etablissements e ON f.etablissement_id = e.id
                WHERE f.actif = 1 
                  AND (f.nom LIKE ? OR f.code LIKE ? OR f.departement LIKE ? 
                       OR f.description LIKE ?)
                LIMIT 10
            ''', (search_pattern, search_pattern, search_pattern, search_pattern))
            
            result['filieres'] = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': result,
            'query': query
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================
# ENDPOINTS - VALIDATION
# ============================================

@api_bp.route('/validate/email', methods=['POST'])
@validate_json('email')
def validate_email():
    """
    POST /api/validate/email
    Vérifie si un email existe déjà dans les préinscriptions
    
    Body:
        {
            "email": "user@example.com"
        }
    
    Response:
        {
            "success": true,
            "available": false,
            "message": "Cet email est déjà utilisé"
        }
    """
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        
        # Validation basique du format email
        if '@' not in email or '.' not in email:
            return jsonify({
                'success': False,
                'error': 'Format d\'email invalide'
            }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM preinscriptions WHERE email = ?', (email,))
        exists = cursor.fetchone() is not None
        conn.close()
        
        return jsonify({
            'success': True,
            'available': not exists,
            'message': 'Cet email est déjà utilisé' if exists else 'Email disponible'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================
# ENDPOINT - HEALTH CHECK
# ============================================

@api_bp.route('/health', methods=['GET'])
def health():
    """
    GET /api/health
    Vérifie l'état de l'API et de la base de données
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT 1')
        cursor.fetchone()
        conn.close()
        
        return jsonify({
            'success': True,
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'database': 'connected',
            'version': '1.0.0'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e)
        }), 500
