"""
Contrôleur de filières
Gère les filières d'études
"""

from flask import request
import sqlite3

DATABASE = 'database/chatbot.db'

def get_db_connection():
    """Crée une connexion à la base de données"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# ============================================
# CONTRÔLEUR - LISTE DES FILIÈRES
# ============================================

def get_filieres():
    """
    Récupère la liste des filières actives
    
    Returns:
        tuple: (response_dict, status_code)
    """
    try:
        # Paramètres de requête
        etablissement_id = request.args.get('etablissement_id', type=int)
        niveau = request.args.get('niveau')
        departement = request.args.get('departement')
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        offset = (page - 1) * per_page
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Construction de la requête
        query = '''
            SELECT 
                f.id, f.nom, f.code, f.niveau, f.departement, f.duree,
                f.frais_inscription, f.frais_scolarite, f.places_disponibles,
                f.description, f.prerequis,
                e.nom as etablissement_nom, e.code as etablissement_code
            FROM filieres f
            JOIN etablissements e ON f.etablissement_id = e.id
            WHERE f.actif = 1
        '''
        params = []
        
        if etablissement_id:
            query += ' AND f.etablissement_id = ?'
            params.append(etablissement_id)
        
        if niveau:
            query += ' AND f.niveau = ?'
            params.append(niveau)
        
        if departement:
            query += ' AND f.departement LIKE ?'
            params.append(f'%{departement}%')
        
        query += ' ORDER BY f.niveau, f.nom LIMIT ? OFFSET ?'
        params.extend([per_page, offset])
        
        filieres = cursor.execute(query, params).fetchall()
        
        # Compter le total
        count_query = 'SELECT COUNT(*) FROM filieres f WHERE f.actif = 1'
        count_params = []
        
        if etablissement_id:
            count_query += ' AND f.etablissement_id = ?'
            count_params.append(etablissement_id)
        
        if niveau:
            count_query += ' AND f.niveau = ?'
            count_params.append(niveau)
        
        if departement:
            count_query += ' AND f.departement LIKE ?'
            count_params.append(f'%{departement}%')
        
        total = cursor.execute(count_query, count_params).fetchone()[0]
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
                'etablissement': {
                    'nom': fil['etablissement_nom'],
                    'code': fil['etablissement_code']
                }
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
        print(f"❌ Erreur dans get_filieres: {e}")
        return {
            'success': False,
            'error': 'Erreur lors de la récupération des filières',
            'code': 'INTERNAL_ERROR'
        }, 500


# ============================================
# CONTRÔLEUR - DÉTAILS D'UNE FILIÈRE
# ============================================

def get_filiere_detail(filiere_id):
    """
    Récupère les détails complets d'une filière
    
    Args:
        filiere_id: ID de la filière
        
    Returns:
        tuple: (response_dict, status_code)
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        filiere = cursor.execute('''
            SELECT 
                f.*,
                e.nom as etablissement_nom, 
                e.code as etablissement_code,
                e.ville, 
                e.telephone, 
                e.email,
                e.site_web
            FROM filieres f
            JOIN etablissements e ON f.etablissement_id = e.id
            WHERE f.id = ?
        ''', (filiere_id,)).fetchone()
        
        if not filiere:
            conn.close()
            return {
                'success': False,
                'error': 'Filière non trouvée',
                'code': 'NOT_FOUND'
            }, 404
        
        # Compter le nombre de préinscriptions
        nb_preinscriptions = cursor.execute(
            'SELECT COUNT(*) FROM preinscriptions WHERE filiere_id = ?',
            (filiere_id,)
        ).fetchone()[0]
        
        conn.close()
        
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
            'actif': filiere['actif'],
            'date_ouverture': filiere['date_ouverture'],
            'date_fermeture': filiere['date_fermeture'],
            'etablissement': {
                'nom': filiere['etablissement_nom'],
                'code': filiere['etablissement_code'],
                'ville': filiere['ville'],
                'telephone': filiere['telephone'],
                'email': filiere['email'],
                'site_web': filiere['site_web']
            },
            'statistiques': {
                'nb_preinscriptions': nb_preinscriptions,
                'places_restantes': max(0, filiere['places_disponibles'] - nb_preinscriptions)
            }
        }
        
        return {
            'success': True,
            'data': result
        }, 200
        
    except Exception as e:
        print(f"❌ Erreur dans get_filiere_detail: {e}")
        return {
            'success': False,
            'error': 'Erreur lors de la récupération des détails',
            'code': 'INTERNAL_ERROR'
        }, 500


# ============================================
# CONTRÔLEUR - FILIÈRES PAR NIVEAU
# ============================================

def get_filieres_by_niveau():
    """
    Récupère les filières groupées par niveau
    
    Returns:
        tuple: (response_dict, status_code)
    """
    try:
        etablissement_id = request.args.get('etablissement_id', type=int)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT 
                f.niveau,
                f.id, f.nom, f.code, f.departement, f.places_disponibles,
                e.nom as etablissement_nom
            FROM filieres f
            JOIN etablissements e ON f.etablissement_id = e.id
            WHERE f.actif = 1
        '''
        params = []
        
        if etablissement_id:
            query += ' AND f.etablissement_id = ?'
            params.append(etablissement_id)
        
        query += ' ORDER BY f.niveau, f.nom'
        
        filieres = cursor.execute(query, params).fetchall()
        conn.close()
        
        # Grouper par niveau
        result = {}
        for fil in filieres:
            niveau = fil['niveau']
            if niveau not in result:
                result[niveau] = []
            
            result[niveau].append({
                'id': fil['id'],
                'nom': fil['nom'],
                'code': fil['code'],
                'departement': fil['departement'],
                'places_disponibles': fil['places_disponibles'],
                'etablissement_nom': fil['etablissement_nom']
            })
        
        return {
            'success': True,
            'data': result,
            'niveaux': list(result.keys())
        }, 200
        
    except Exception as e:
        print(f"❌ Erreur dans get_filieres_by_niveau: {e}")
        return {
            'success': False,
            'error': 'Erreur lors de la récupération des filières par niveau',
            'code': 'INTERNAL_ERROR'
        }, 500
