"""
Chatbot de Préinscription Universitaire
Application Flask principale
Auteur: Madick Ange César
Date: Novembre 2025
"""

from flask import Flask, redirect, render_template, request, jsonify, session, url_for
from flask_cors import CORS
from datetime import datetime, timedelta
import os
import json
import sqlite3
from werkzeug.utils import secure_filename
import secrets

# Importer les Blueprints
from route.api import api_bp
from route.auth_api import auth_bp

# Importer le module Gemini AI
from model.gemini_chatbot import generate_response, get_fallback_response, conversation_context

# Configuration de l'application
app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'jpg', 'jpeg', 'png'}
app.config['DATABASE'] = 'database/chatbot.db'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

# Enable CORS
CORS(app)

# Enregistrer les Blueprints
app.register_blueprint(api_bp)
app.register_blueprint(auth_bp)

# Add CSP headers to allow inline scripts
@app.after_request
def add_security_headers(response):
    response.headers['Content-Security-Policy'] = "script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com https://fonts.googleapis.com; style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com https://fonts.googleapis.com; font-src 'self' https://cdnjs.cloudflare.com https://fonts.gstatic.com;"
    return response

# Créer le dossier uploads s'il n'existe pas
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('database', exist_ok=True)

# ============================================
# UTILITAIRES BASE DE DONNÉES
# ============================================

def get_db_connection():
    """Crée une connexion à la base de données"""
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initialise la base de données avec toutes les tables selon le diagramme ER"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Active les contraintes de clés étrangères
    cursor.execute("PRAGMA foreign_keys = ON")
    
    # Table établissements
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS etablissements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            code TEXT UNIQUE NOT NULL,
            adresse TEXT,
            ville TEXT,
            telephone TEXT,
            email TEXT,
            site_web TEXT,
            type TEXT CHECK(type IN ('université', 'école', 'institut')),
            actif INTEGER DEFAULT 1,
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Table filières
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS filieres (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            etablissement_id INTEGER NOT NULL,
            nom TEXT NOT NULL,
            code TEXT NOT NULL,
            niveau TEXT CHECK(niveau IN ('Licence', 'Master', 'Doctorat')),
            departement TEXT,
            duree INTEGER,
            frais_inscription REAL DEFAULT 0,
            frais_scolarite REAL DEFAULT 0,
            places_disponibles INTEGER DEFAULT 0,
            description TEXT,
            prerequis TEXT,
            actif INTEGER DEFAULT 1,
            date_ouverture TIMESTAMP,
            date_fermeture TIMESTAMP,
            FOREIGN KEY (etablissement_id) REFERENCES etablissements(id) ON DELETE CASCADE,
            UNIQUE(etablissement_id, code)
        )
    ''')
    
    # Table users
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            prenom TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            telephone TEXT,
            password_hash TEXT,
            role TEXT DEFAULT 'visiteur' CHECK(role IN ('admin', 'etudiant', 'visiteur')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Table chat_sessions
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT UNIQUE NOT NULL,
            user_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            metadata TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
        )
    ''')
    
    # Table messages
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('user', 'bot')),
            contenu TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            metadata TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
            FOREIGN KEY (session_id) REFERENCES chat_sessions(session_id) ON DELETE CASCADE
        )
    ''')
    
    # Table preinscriptions (mise à jour avec les nouvelles références)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS preinscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            etablissement_id INTEGER NOT NULL,
            filiere_id INTEGER NOT NULL,
            nom TEXT NOT NULL,
            prenom TEXT NOT NULL,
            email TEXT NOT NULL,
            telephone TEXT NOT NULL,
            date_naissance TEXT,
            lieu_naissance TEXT,
            adresse TEXT,
            niveau TEXT,
            motivation TEXT,
            photo_path TEXT,
            diplome_path TEXT,
            releve_path TEXT,
            cv_path TEXT,
            statut TEXT DEFAULT 'nouveau' CHECK(statut IN ('nouveau', 'en_cours', 'validé', 'rejeté')),
            accept_terms INTEGER DEFAULT 0,
            newsletter INTEGER DEFAULT 0,
            date_soumission TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            meta_json TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
            FOREIGN KEY (etablissement_id) REFERENCES etablissements(id) ON DELETE RESTRICT,
            FOREIGN KEY (filiere_id) REFERENCES filieres(id) ON DELETE RESTRICT
        )
    ''')
    
    # Créer les index
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_filieres_etablissement ON filieres(etablissement_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_preinscriptions_etablissement ON preinscriptions(etablissement_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_preinscriptions_filiere ON preinscriptions(filiere_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id)")
    
    # Insérer des données de test si la table établissements est vide
    cursor.execute("SELECT COUNT(*) FROM etablissements")
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO etablissements (nom, code, adresse, ville, telephone, email, site_web, type, actif)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', ('ICT University', 'ICTU', 'Avenue de la République', 'Yaoundé', 
              '+237 6XX XXX XXX', 'contact@ictuniversity.cm', 'https://ictuniversity.cm', 'université', 1))
        
        etablissement_id = cursor.lastrowid
        
        # Ajouter des filières
        filieres = [
            (etablissement_id, 'Licence en Informatique Générale', 'L-INFO', 'Licence', 'Informatique', 3, 25000, 450000, 50, 
             'Formation complète en informatique', 'BAC série C, D ou E', 1),
            (etablissement_id, 'Licence en Génie Logiciel', 'L-GL', 'Licence', 'Informatique', 3, 25000, 450000, 40,
             'Architecture logicielle et DevOps', 'BAC série C, D ou E', 1),
            (etablissement_id, 'Master en Intelligence Artificielle', 'M-IA', 'Master', 'Informatique', 2, 35000, 650000, 25,
             'IA et Data Science', 'Licence en Informatique', 1),
        ]
        
        for filiere in filieres:
            cursor.execute('''
                INSERT INTO filieres (etablissement_id, nom, code, niveau, departement, duree, 
                                     frais_inscription, frais_scolarite, places_disponibles, description, prerequis, actif)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', filiere)
    
    conn.commit()
    conn.close()
    print("✅ Base de données initialisée avec succès!")

# Initialiser la base de données au démarrage
init_database()

# ============================================
# UTILITAIRES FICHIERS
# ============================================

def allowed_file(filename):
    """Vérifie si le fichier a une extension autorisée"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def save_file(file, prefix=''):
    """Sauvegarde un fichier uploadé de manière sécurisée"""
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Ajouter un timestamp pour éviter les conflits
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{prefix}_{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return filepath
    return None

# ============================================
# LOGIQUE DU CHATBOT (Simple - À améliorer avec votre modèle IA)
# ============================================

def get_bot_response(message, session_id):
    """
    Génère une réponse du chatbot basée sur le message de l'utilisateur
    TODO: Remplacer par votre modèle IA personnalisé
    """
    message_lower = message.lower()
    
    # Réponses basiques basées sur des mots-clés
    responses = {
        'programmes': """
Nous proposons plusieurs programmes d'excellence :

📚 **Informatique** - Développement logiciel et systèmes
🧠 **IA & Machine Learning** - Intelligence artificielle et données
🔌 **Internet des Objets (IoT)** - Systèmes connectés et embarqués
🛡️ **Cybersécurité** - Sécurité des systèmes informatiques
📊 **Data Science** - Analyse et visualisation de données
🌐 **Réseaux & Télécoms** - Infrastructure et communication

Souhaitez-vous plus d'informations sur un programme spécifique ?
        """,
        
        'documents': """
📄 **Documents requis pour votre préinscription :**

✅ Photo d'identité récente
✅ Copie du dernier diplôme obtenu
✅ Relevé de notes (optionnel mais recommandé)
✅ CV (pour les niveaux Master)
✅ Lettre de motivation (optionnelle)

**Formats acceptés :** PDF, JPG, PNG (max 5 Mo par fichier)

Vous pouvez soumettre ces documents via notre formulaire de préinscription.
        """,
        
        'frais': """
💰 **Frais de scolarité 2025-2026 :**

**Licence :**
- L1 : 350 000 FCFA/an
- L2 : 400 000 FCFA/an
- L3 : 450 000 FCFA/an

**Master :**
- M1 : 500 000 FCFA/an
- M2 : 550 000 FCFA/an

💡 **Facilités de paiement disponibles**
🎓 **Bourses d'excellence pour les meilleurs étudiants**

Des questions sur les frais ?
        """,
        
        'inscription': """
📝 **Procédure d'inscription en 3 étapes :**

1️⃣ **Préinscription en ligne**
   - Remplissez le formulaire de préinscription
   - Soumettez les documents requis

2️⃣ **Validation du dossier**
   - Notre équipe examine votre dossier (2-5 jours)
   - Vous recevez un email de confirmation

3️⃣ **Finalisation**
   - Payez les frais d'inscription
   - Recevez votre carte d'étudiant

🚀 Vous pouvez commencer maintenant en remplissant le formulaire de préinscription !
        """,
        
        'contact': """
📞 **Contactez-nous :**

📧 **Email :** contact@ict-university.cm
📱 **Téléphone :** +237 6XX XXX XXX
📍 **Adresse :** Yaoundé, Cameroun

⏰ **Horaires :**
- Lundi - Vendredi : 8h - 17h
- Samedi : 9h - 13h

💬 **Chat en ligne :** 24/7 (vous y êtes déjà !)

Comment puis-je vous aider davantage ?
        """,
        
        'aide': """
🤖 **Je peux vous aider avec :**

✅ Informations sur les programmes
✅ Documents nécessaires
✅ Frais de scolarité
✅ Procédure d'inscription
✅ Formulaire de préinscription
✅ Contacts et localisation

Posez-moi simplement votre question, je suis là pour vous aider ! 😊
        """
    }
    
    # Recherche de mots-clés dans le message
    if any(word in message_lower for word in ['programme', 'formation', 'étude', 'cours', 'filière']):
        return responses['programmes']
    elif any(word in message_lower for word in ['document', 'pièce', 'dossier', 'fichier']):
        return responses['documents']
    elif any(word in message_lower for word in ['frais', 'coût', 'prix', 'paiement', 'montant', 'tarif']):
        return responses['frais']
    elif any(word in message_lower for word in ['inscription', 'inscrire', 'inscrit', 'préinscription']):
        return responses['inscription']
    elif any(word in message_lower for word in ['contact', 'appeler', 'téléphone', 'email', 'adresse']):
        return responses['contact']
    elif any(word in message_lower for word in ['aide', 'aider', 'bonjour', 'salut', 'hello']):
        return responses['aide']
    else:
        # Réponse par défaut
        return """
Je suis là pour vous aider ! Voici quelques sujets sur lesquels je peux vous renseigner :

📚 Programmes disponibles
📄 Documents requis
💰 Frais de scolarité
📝 Procédure d'inscription
📞 Contact

Qu'aimeriez-vous savoir ?
        """

# ============================================
# ROUTES - PAGES WEB
# ============================================

@app.route('/')
def index():
    """Page d'accueil"""
    return render_template('index.html')

@app.route('/login')
def login():
    """Page de connexion"""
    # Rediriger si déjà connecté
    if 'user_id' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('chat'))
    return render_template('login.html')

@app.route('/register')
def register():
    """Page d'inscription"""
    # Rediriger si déjà connecté
    if 'user_id' in session:
        return redirect(url_for('chat'))
    return render_template('register.html')

@app.route('/profile')
def profile():
    """Page de profil utilisateur"""
    # Vérifier l'authentification
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('profile.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    """Tableau de bord administrateur"""
    # Vérifier l'authentification et le rôle admin
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if session.get('role') != 'admin':
        return render_template('error.html', 
                             message="Accès refusé. Vous devez être administrateur.",
                             code=403), 403
    return render_template('admin_dashboard.html')

@app.route('/chat')
def chat():
    """Interface du chatbot"""
    # Vérifier l'authentification
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Créer une nouvelle session si elle n'existe pas
    if 'chat_session_id' not in session:
        session['chat_session_id'] = secrets.token_hex(16)
        
        # Enregistrer la session dans la BD
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO chat_sessions (session_id) VALUES (?)',
            (session['chat_session_id'],)
        )
        conn.commit()
        conn.close()
    
    return render_template('chat.html')

@app.route('/preinscription')
def preinscription():
    """Formulaire de préinscription"""
    # Vérifier l'authentification
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('preinscription.html')

# ============================================
# ROUTES - API
# ============================================

@app.route('/api/message', methods=['POST'])
def api_message():
    """Endpoint pour recevoir et répondre aux messages du chatbot"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({'error': 'Message requis'}), 400
        
        message = data.get('message', '').strip()
        session_id = data.get('session_id') or session.get('chat_session_id', 'default')
        
        if not message:
            return jsonify({'error': 'Message vide'}), 400
        
        # Sauvegarder le message de l'utilisateur
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO messages (session_id, role, contenu) VALUES (?, ?, ?)',
            (session_id, 'user', message)
        )
        conn.commit()
        
        # Récupérer le nom de l'utilisateur si connecté
        user_name = None
        if 'user_id' in session:
            try:
                user = conn.execute(
                    'SELECT prenom, nom FROM users WHERE id = ?',
                    (session['user_id'],)
                ).fetchone()
                if user:
                    user_name = f"{user['prenom']} {user['nom']}"
            except:
                pass
        
        # Générer la réponse avec Gemini AI
        try:
            bot_response = generate_response(message, session_id, user_name)
        except Exception as e:
            print(f"⚠️ Erreur Gemini, utilisation fallback: {e}")
            # Fallback vers l'ancienne fonction en cas d'erreur
            bot_response = get_bot_response(message, session_id)
        
        # Sauvegarder la réponse du bot
        conn.execute(
            'INSERT INTO messages (session_id, role, contenu) VALUES (?, ?, ?)',
            (session_id, 'bot', bot_response)
        )
        conn.commit()
        
        # Mettre à jour l'activité de la session
        conn.execute(
            'UPDATE chat_sessions SET last_activity = CURRENT_TIMESTAMP WHERE session_id = ?',
            (session_id,)
        )
        conn.commit()
        conn.close()
        
        return jsonify({
            'response': bot_response,
            'session_id': session_id,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"❌ Erreur dans api_message: {e}")
        return jsonify({'error': 'Erreur serveur', 'message': str(e)}), 500

@app.route('/api/preinscription', methods=['POST'])
def api_preinscription():
    """Endpoint pour soumettre le formulaire de préinscription"""
    try:
        # Vérifier l'authentification
        if 'user_id' not in session:
            return jsonify({
                'success': False,
                'message': 'Vous devez être connecté pour faire une préinscription'
            }), 401
        
        user_id = session['user_id']
        
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
        if not all([nom, prenom, email, telephone, date_naissance, lieu_naissance, 
                    adresse, programme, niveau]):
            return jsonify({
                'success': False,
                'message': 'Tous les champs obligatoires doivent être remplis'
            }), 400
        
        if not accept_terms:
            return jsonify({
                'success': False,
                'message': 'Vous devez accepter les conditions générales'
            }), 400
        
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
        
        # Métadonnées supplémentaires
        metadata = {
            'user_id': user_id,
            'user_email': session.get('email'),
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
        cursor.execute("SELECT id FROM filieres WHERE nom LIKE ? OR code LIKE ? LIMIT 1", 
                      (f'%{programme}%', f'%{programme}%'))
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
        
        return jsonify({
            'success': True,
            'message': 'Préinscription enregistrée avec succès !',
            'preinscription_id': preinscription_id,
            'email_confirmation': f'Un email de confirmation a été envoyé à {email}'
        })
        
    except sqlite3.IntegrityError as e:
        print(f"❌ Erreur d'intégrité: {e}")
        return jsonify({
            'success': False,
            'message': 'Cette adresse email est déjà enregistrée'
        }), 409
        
    except Exception as e:
        print(f"❌ Erreur dans api_preinscription: {e}")
        return jsonify({
            'success': False,
            'message': 'Erreur lors de l\'enregistrement',
            'error': str(e)
        }), 500

@app.route('/api/preinscriptions', methods=['GET'])
def api_get_preinscriptions():
    """Endpoint pour récupérer la liste des préinscriptions (admin)"""
    try:
        # TODO: Ajouter l'authentification admin ici
        
        conn = get_db_connection()
        preinscriptions = conn.execute('''
            SELECT id, nom, prenom, email, telephone, programme, niveau, 
                   statut, date_soumission
            FROM preinscriptions
            ORDER BY date_soumission DESC
        ''').fetchall()
        conn.close()
        
        # Convertir en liste de dictionnaires
        result = []
        for row in preinscriptions:
            result.append({
                'id': row['id'],
                'nom': row['nom'],
                'prenom': row['prenom'],
                'email': row['email'],
                'telephone': row['telephone'],
                'programme': row['programme'],
                'niveau': row['niveau'],
                'statut': row['statut'],
                'date_soumission': row['date_soumission']
            })
        
        return jsonify({
            'success': True,
            'count': len(result),
            'preinscriptions': result
        })
        
    except Exception as e:
        print(f"❌ Erreur dans api_get_preinscriptions: {e}")
        return jsonify({
            'success': False,
            'message': 'Erreur lors de la récupération',
            'error': str(e)
        }), 500

@app.route('/api/messages/history/<session_id>', methods=['GET'])
def api_get_message_history(session_id):
    """Récupère l'historique des messages pour une session"""
    try:
        conn = get_db_connection()
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
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'messages': result
        })
        
    except Exception as e:
        print(f"❌ Erreur dans api_get_message_history: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================
# ROUTES API - ÉTABLISSEMENTS & FILIÈRES
# ============================================

@app.route('/api/etablissements', methods=['GET'])
def api_get_etablissements():
    """Récupère la liste de tous les établissements actifs"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, nom, code, ville, type, telephone, email, site_web
            FROM etablissements
            WHERE actif = 1
            ORDER BY nom
        ''')
        
        etablissements = cursor.fetchall()
        conn.close()
        
        result = []
        for etab in etablissements:
            result.append({
                'id': etab['id'],
                'nom': etab['nom'],
                'code': etab['code'],
                'ville': etab['ville'],
                'type': etab['type'],
                'telephone': etab['telephone'],
                'email': etab['email'],
                'site_web': etab['site_web']
            })
        
        return jsonify({
            'success': True,
            'etablissements': result,
            'total': len(result)
        })
        
    except Exception as e:
        print(f"❌ Erreur dans api_get_etablissements: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/filieres', methods=['GET'])
def api_get_filieres():
    """Récupère la liste des filières actives (optionnel: filtrées par établissement)"""
    try:
        etablissement_id = request.args.get('etablissement_id', type=int)
        niveau = request.args.get('niveau')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT f.id, f.nom, f.code, f.niveau, f.departement, f.duree,
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
        
        query += ' ORDER BY f.niveau, f.nom'
        
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
                'etablissement': {
                    'nom': fil['etablissement_nom'],
                    'code': fil['etablissement_code']
                }
            })
        
        return jsonify({
            'success': True,
            'filieres': result,
            'total': len(result)
        })
        
    except Exception as e:
        print(f"❌ Erreur dans api_get_filieres: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/filieres/<int:filiere_id>', methods=['GET'])
def api_get_filiere_detail(filiere_id):
    """Récupère les détails complets d'une filière"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT f.*, e.nom as etablissement_nom, e.ville, e.telephone, e.email
            FROM filieres f
            JOIN etablissements e ON f.etablissement_id = e.id
            WHERE f.id = ?
        ''', (filiere_id,))
        
        filiere = cursor.fetchone()
        conn.close()
        
        if not filiere:
            return jsonify({
                'success': False,
                'message': 'Filière non trouvée'
            }), 404
        
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
                'ville': filiere['ville'],
                'telephone': filiere['telephone'],
                'email': filiere['email']
            }
        }
        
        return jsonify({
            'success': True,
            'filiere': result
        })
        
    except Exception as e:
        print(f"❌ Erreur dans api_get_filiere_detail: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================
# ROUTES - UTILITAIRES
# ============================================

@app.route('/health')
def health():
    """Endpoint de santé pour vérifier que l'application fonctionne"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0'
    })

@app.errorhandler(404)
def not_found(error):
    """Gestion des erreurs 404"""
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Gestion des erreurs 500"""
    return jsonify({
        'error': 'Erreur interne du serveur',
        'message': str(error)
    }), 500

# ============================================
# POINT D'ENTRÉE
# ============================================

if __name__ == '__main__':
    print("🚀 Démarrage de l'application Chatbot de Préinscription...")
    print("📊 Base de données: OK")
    print("🌐 Serveur: http://127.0.0.1:5000")
    print("💬 Chat: http://127.0.0.1:5000/chat")
    print("📝 Formulaire: http://127.0.0.1:5000/preinscription")
    print("\n✨ Application prête !")
    
    app.run(debug=True, host='0.0.0.0', port=5000)