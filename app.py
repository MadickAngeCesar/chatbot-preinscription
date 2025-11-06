"""
Chatbot de Préinscription Universitaire - Version 3.0
Application Flask avec architecture MVC + Controllers
Auteur: Madick Ange César
Date: Novembre 2025
"""

from flask import Flask, redirect, render_template, session, url_for
from flask_cors import CORS
from datetime import timedelta
import secrets
import os

# Importer les middlewares
from middleware import (
    init_auth_middleware,
    init_validation_middleware,
    init_logging_middleware,
    init_error_handlers
)

# Importer les routes (blueprints)
from route import auth_bp, api_bp

# ============================================
# CONFIGURATION DE L'APPLICATION
# ============================================

app = Flask(__name__)

# Configuration de base
# Prefer a fixed secret in production provided via env var. Fall back to generated token for dev.
app.secret_key = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'jpg', 'jpeg', 'png'}
app.config['DATABASE'] = 'database/chatbot.db'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

# Enable CORS
CORS(app, supports_credentials=True)

# Créer les dossiers nécessaires
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('database', exist_ok=True)
os.makedirs('logs', exist_ok=True)

# ============================================
# INITIALISATION DES MIDDLEWARES
# ============================================

print("🔧 Initialisation des middlewares...")
init_auth_middleware(app)
init_validation_middleware(app)
init_logging_middleware(app)
init_error_handlers(app)
print("✅ Middlewares initialisés avec succès")

# ============================================
# ENREGISTREMENT DES BLUEPRINTS
# ============================================

print("📋 Enregistrement des routes...")
app.register_blueprint(auth_bp)
app.register_blueprint(api_bp)
print("✅ Routes enregistrées avec succès")

# ============================================
# ROUTES - PAGES WEB (VUES)
# ============================================

@app.route('/')
def index():
    """Page d'accueil"""
    return render_template('index.html')


@app.route('/login')
def login():
    """Page de connexion"""
    if 'user_id' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('chat'))
    return render_template('login.html')


@app.route('/register')
def register():
    """Page d'inscription"""
    if 'user_id' in session:
        return redirect(url_for('chat'))
    return render_template('register.html')


@app.route('/profile')
def profile():
    """Page de profil utilisateur"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('profile.html')


@app.route('/admin/dashboard')
def admin_dashboard():
    """Tableau de bord administrateur"""
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
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Créer une session de chat si nécessaire
    if 'chat_session_id' not in session:
        import sqlite3
        session['chat_session_id'] = secrets.token_hex(16)
        
        # Enregistrer la session dans la BD
        conn = sqlite3.connect(app.config['DATABASE'])
        conn.row_factory = sqlite3.Row
        conn.execute(
            'INSERT INTO chat_sessions (session_id, user_id) VALUES (?, ?)',
            (session['chat_session_id'], session['user_id'])
        )
        conn.commit()
        conn.close()
    
    return render_template('chat.html')


@app.route('/preinscription')
def preinscription():
    """Formulaire de préinscription"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('preinscription.html')


# ============================================
# ROUTE - HEALTH CHECK
# ============================================

@app.route('/health')
def health():
    """Endpoint de santé pour vérifier que l'application fonctionne"""
    from datetime import datetime
    from flask import jsonify
    
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '3.0.0',
        'architecture': 'MVC with Controllers and Middleware'
    }), 200


# ============================================
# INITIALISATION DE LA BASE DE DONNÉES
# ============================================

def init_database():
    """Initialise la base de données avec toutes les tables"""
    import sqlite3
    
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
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
    
    # Table preinscriptions
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
# POINT D'ENTRÉE
# ============================================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 Chatbot de Préinscription Universitaire v3.0")
    print("="*60)
    print("📊 Base de données: OK")
    print("🔐 Middlewares: OK")
    print("📋 Routes: OK")
    print("🌐 Serveur: http://127.0.0.1:5000")
    print("💬 Chat: http://127.0.0.1:5000/chat")
    print("📝 Formulaire: http://127.0.0.1:5000/preinscription")
    print("📖 API Docs: Voir doc/API-ARCHITECTURE.md")
    print("="*60)
    print("\n✨ Application prête ! Architecture MVC avec Controllers\n")
    
    app.run(debug=False, host='0.0.0.0', port=5000)
