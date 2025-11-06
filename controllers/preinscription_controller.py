"""
Contrôleur de préinscription
Gère les demandes de préinscription universitaire
"""

from flask import request, g
from datetime import datetime
from werkzeug.utils import secure_filename
import sqlite3
import json
import os

from middleware import ValidationError, log_user_action

DATABASE = 'database/chatbot.db'
UPLOAD_FOLDER = 'uploads'

def get_db_connection():
    """Crée une connexion à la base de données"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def allowed_file(filename, allowed_extensions={'pdf', 'jpg', 'jpeg', 'png'}):
    """Vérifie si le fichier a une extension autorisée"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def save_file(file, prefix=''):
    """Sauvegarde un fichier uploadé de manière sécurisée"""
    if file and file.filename and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{prefix}_{timestamp}_{filename}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        return filepath
    return None

# ============================================
# CONTRÔLEUR - CRÉATION DE PRÉINSCRIPTION
# ============================================

def create_preinscription():
    """
    Crée une nouvelle demande de préinscription
    
    Returns:
        tuple: (response_dict, status_code)
    """
    try:
        user_id = g.user_id
        
        # Récupérer les données du formulaire
        nom = request.form.get('nom', '').strip()
        prenom = request.form.get('prenom', '').strip()
        email = request.form.get('email', '').strip()
        telephone = request.form.get('telephone', '').strip()
        date_naissance = request.form.get('dateNaissance', '').strip()
        lieu_naissance = request.form.get('lieuNaissance', '').strip()
        adresse = request.form.get('adresse', '').strip()
        programme = request.form.get('programme', '').strip()
        niveau = request.form.get('niveau', '').strip()
        motivation = request.form.get('motivation', '').strip()
        accept_terms = request.form.get('acceptTerms') == 'on'
        newsletter = request.form.get('newsletter') == 'on'
        
        # Validation des champs obligatoires
        required_fields = {
            'nom': nom,
            'prenom': prenom,
            'email': email,
            'telephone': telephone,
            'date_naissance': date_naissance,
            'lieu_naissance': lieu_naissance,
            'adresse': adresse,
            'programme': programme,
            'niveau': niveau
        }
        
        missing = [k for k, v in required_fields.items() if not v]
        if missing:
            raise ValidationError(f'Champs requis manquants: {", ".join(missing)}')
        
        if not accept_terms:
            raise ValidationError('Vous devez accepter les conditions d\'utilisation')
        
        # Traiter les fichiers uploadés
        photo_path = None
        diplome_path = None
        releve_path = None
        cv_path = None
        
        if 'photo' in request.files:
            photo = request.files['photo']
            if photo.filename:
                photo_path = save_file(photo, 'photo')
        
        if 'diplome' in request.files:
            diplome = request.files['diplome']
            if diplome.filename:
                diplome_path = save_file(diplome, 'diplome')
        
        if 'releve' in request.files:
            releve = request.files['releve']
            if releve.filename:
                releve_path = save_file(releve, 'releve')
        
        if 'cv' in request.files:
            cv = request.files['cv']
            if cv.filename:
                cv_path = save_file(cv, 'cv')
        
        # Métadonnées
        metadata = {
            'user_id': user_id,
            'user_email': g.user_email if hasattr(g, 'user_email') else email,
            'user_agent': request.headers.get('User-Agent'),
            'ip_address': request.remote_addr,
            'submitted_at': datetime.now().isoformat()
        }
        
        # Insérer dans la base de données
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Récupérer l'établissement par défaut (ICT University)
        cursor.execute("SELECT id FROM etablissements WHERE code = 'ICTU' LIMIT 1")
        etab_row = cursor.fetchone()
        etablissement_id = etab_row[0] if etab_row else 1
        
        # Trouver la filière correspondante au programme
        cursor.execute(
            "SELECT id FROM filieres WHERE nom LIKE ? OR code LIKE ? LIMIT 1",
            (f'%{programme}%', f'%{programme}%')
        )
        filiere_row = cursor.fetchone()
        filiere_id = filiere_row[0] if filiere_row else 1
        
        cursor.execute('''
            INSERT INTO preinscriptions (
                etablissement_id, filiere_id, user_id,
                nom, prenom, email, telephone, date_naissance, lieu_naissance,
                adresse, niveau, motivation, photo_path, diplome_path,
                releve_path, cv_path, accept_terms, newsletter, meta_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            etablissement_id, filiere_id, user_id,
            nom, prenom, email, telephone, date_naissance, lieu_naissance,
            adresse, niveau, motivation, photo_path, diplome_path,
            releve_path, cv_path, accept_terms, newsletter, json.dumps(metadata)
        ))
        
        preinscription_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        log_user_action('CREATE_PREINSCRIPTION', user_id, {
            'preinscription_id': preinscription_id,
            'programme': programme,
            'niveau': niveau
        })
        
        return {
            'success': True,
            'message': 'Préinscription enregistrée avec succès !',
            'preinscription_id': preinscription_id,
            'email_confirmation': f'Un email de confirmation a été envoyé à {email}'
        }, 201
        
    except ValidationError as e:
        return {
            'success': False,
            'error': e.message,
            'code': e.code
        }, e.status_code
    
    except sqlite3.IntegrityError as e:
        print(f"❌ Erreur d'intégrité: {e}")
        return {
            'success': False,
            'error': 'Cette adresse email est déjà enregistrée',
            'code': 'DUPLICATE_EMAIL'
        }, 409
    
    except Exception as e:
        print(f"❌ Erreur dans create_preinscription: {e}")
        return {
            'success': False,
            'error': 'Erreur lors de l\'enregistrement de la préinscription',
            'code': 'INTERNAL_ERROR'
        }, 500


# ============================================
# CONTRÔLEUR - RÉCUPÉRATION DES PRÉINSCRIPTIONS
# ============================================

def get_preinscriptions():
    """
    Récupère la liste des préinscriptions
    (Admin: toutes, Utilisateur: ses propres préinscriptions)
    
    Returns:
        tuple: (response_dict, status_code)
    """
    try:
        user_id = g.user_id
        user_role = g.user_role if hasattr(g, 'user_role') else 'visiteur'
        
        # Paramètres de pagination
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        offset = (page - 1) * per_page
        
        # Filtres
        statut = request.args.get('statut')
        niveau = request.args.get('niveau')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Construction de la requête selon le rôle
        base_query = '''
            SELECT 
                p.id, p.nom, p.prenom, p.email, p.telephone, p.niveau,
                p.statut, p.date_soumission,
                f.nom as filiere_nom, f.code as filiere_code,
                e.nom as etablissement_nom
            FROM preinscriptions p
            LEFT JOIN filieres f ON p.filiere_id = f.id
            LEFT JOIN etablissements e ON p.etablissement_id = e.id
        '''
        
        where_clauses = []
        params = []
        
        # Si non admin, filtrer par user_id
        if user_role != 'admin':
            where_clauses.append('p.user_id = ?')
            params.append(user_id)
        
        if statut:
            where_clauses.append('p.statut = ?')
            params.append(statut)
        
        if niveau:
            where_clauses.append('p.niveau = ?')
            params.append(niveau)
        
        if where_clauses:
            base_query += ' WHERE ' + ' AND '.join(where_clauses)
        
        base_query += ' ORDER BY p.date_soumission DESC LIMIT ? OFFSET ?'
        params.extend([per_page, offset])
        
        preinscriptions = cursor.execute(base_query, params).fetchall()
        
        # Compter le total
        count_query = 'SELECT COUNT(*) FROM preinscriptions p'
        if where_clauses:
            count_query += ' WHERE ' + ' AND '.join(where_clauses[:-2] if len(params) > 2 else where_clauses)
        
        total = cursor.execute(count_query, params[:-2] if len(params) > 2 else params).fetchone()[0]
        conn.close()
        
        result = []
        for row in preinscriptions:
            result.append({
                'id': row['id'],
                'nom': row['nom'],
                'prenom': row['prenom'],
                'email': row['email'],
                'telephone': row['telephone'],
                'niveau': row['niveau'],
                'statut': row['statut'],
                'date_soumission': row['date_soumission'],
                'filiere': {
                    'nom': row['filiere_nom'],
                    'code': row['filiere_code']
                },
                'etablissement': {
                    'nom': row['etablissement_nom']
                }
            })
        
        return {
            'success': True,
            'preinscriptions': result,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        }, 200
        
    except Exception as e:
        print(f"❌ Erreur dans get_preinscriptions: {e}")
        return {
            'success': False,
            'error': 'Erreur lors de la récupération des préinscriptions',
            'code': 'INTERNAL_ERROR'
        }, 500


# ============================================
# CONTRÔLEUR - DÉTAILS D'UNE PRÉINSCRIPTION
# ============================================

def get_preinscription_detail(preinscription_id):
    """
    Récupère les détails d'une préinscription spécifique
    
    Args:
        preinscription_id: ID de la préinscription
        
    Returns:
        tuple: (response_dict, status_code)
    """
    try:
        user_id = g.user_id
        user_role = g.user_role if hasattr(g, 'user_role') else 'visiteur'
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        preinscription = cursor.execute('''
            SELECT 
                p.*,
                f.nom as filiere_nom, f.code as filiere_code, f.niveau as filiere_niveau,
                e.nom as etablissement_nom, e.ville as etablissement_ville
            FROM preinscriptions p
            LEFT JOIN filieres f ON p.filiere_id = f.id
            LEFT JOIN etablissements e ON p.etablissement_id = e.id
            WHERE p.id = ?
        ''', (preinscription_id,)).fetchone()
        
        conn.close()
        
        if not preinscription:
            return {
                'success': False,
                'error': 'Préinscription non trouvée',
                'code': 'NOT_FOUND'
            }, 404
        
        # Vérifier les permissions (non-admin ne peut voir que ses propres préinscriptions)
        if user_role != 'admin' and preinscription['user_id'] != user_id:
            return {
                'success': False,
                'error': 'Accès non autorisé',
                'code': 'FORBIDDEN'
            }, 403
        
        result = {
            'id': preinscription['id'],
            'nom': preinscription['nom'],
            'prenom': preinscription['prenom'],
            'email': preinscription['email'],
            'telephone': preinscription['telephone'],
            'date_naissance': preinscription['date_naissance'],
            'lieu_naissance': preinscription['lieu_naissance'],
            'adresse': preinscription['adresse'],
            'niveau': preinscription['niveau'],
            'motivation': preinscription['motivation'],
            'statut': preinscription['statut'],
            'date_soumission': preinscription['date_soumission'],
            'documents': {
                'photo': preinscription['photo_path'],
                'diplome': preinscription['diplome_path'],
                'releve': preinscription['releve_path'],
                'cv': preinscription['cv_path']
            },
            'filiere': {
                'nom': preinscription['filiere_nom'],
                'code': preinscription['filiere_code'],
                'niveau': preinscription['filiere_niveau']
            },
            'etablissement': {
                'nom': preinscription['etablissement_nom'],
                'ville': preinscription['etablissement_ville']
            }
        }
        
        return {
            'success': True,
            'preinscription': result
        }, 200
        
    except Exception as e:
        print(f"❌ Erreur dans get_preinscription_detail: {e}")
        return {
            'success': False,
            'error': 'Erreur lors de la récupération des détails',
            'code': 'INTERNAL_ERROR'
        }, 500


# ============================================
# CONTRÔLEUR - MISE À JOUR DU STATUT (ADMIN)
# ============================================

def update_preinscription_status(preinscription_id):
    """
    Met à jour le statut d'une préinscription (admin uniquement)
    
    Args:
        preinscription_id: ID de la préinscription
        
    Returns:
        tuple: (response_dict, status_code)
    """
    try:
        data = request.get_json()
        nouveau_statut = data.get('statut', '').strip()
        
        # Valider le statut
        statuts_valides = ['nouveau', 'en_cours', 'validé', 'rejeté']
        if nouveau_statut not in statuts_valides:
            raise ValidationError(f'Statut invalide. Valeurs autorisées: {", ".join(statuts_valides)}')
        
        conn = get_db_connection()
        
        # Vérifier que la préinscription existe
        preinscription = conn.execute(
            'SELECT id FROM preinscriptions WHERE id = ?',
            (preinscription_id,)
        ).fetchone()
        
        if not preinscription:
            conn.close()
            return {
                'success': False,
                'error': 'Préinscription non trouvée',
                'code': 'NOT_FOUND'
            }, 404
        
        # Mettre à jour le statut
        conn.execute(
            'UPDATE preinscriptions SET statut = ? WHERE id = ?',
            (nouveau_statut, preinscription_id)
        )
        conn.commit()
        conn.close()
        
        log_user_action('UPDATE_PREINSCRIPTION_STATUS', g.user_id, {
            'preinscription_id': preinscription_id,
            'nouveau_statut': nouveau_statut
        })
        
        return {
            'success': True,
            'message': 'Statut mis à jour avec succès',
            'preinscription_id': preinscription_id,
            'statut': nouveau_statut
        }, 200
        
    except ValidationError as e:
        return {
            'success': False,
            'error': e.message,
            'code': e.code
        }, e.status_code
    
    except Exception as e:
        print(f"❌ Erreur dans update_preinscription_status: {e}")
        return {
            'success': False,
            'error': 'Erreur lors de la mise à jour du statut',
            'code': 'INTERNAL_ERROR'
        }, 500
