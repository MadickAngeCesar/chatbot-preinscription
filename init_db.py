import os
import sqlite3
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, "database")
DB_PATH = os.path.join(DB_DIR, "chatbot.db")

def init_db():
    """Initialise la base de données avec toutes les tables selon le diagramme ER"""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Active les contraintes de clés étrangères
    cur.execute("PRAGMA foreign_keys = ON")
    
    # ========================================
    # TABLE: ETABLISSEMENTS
    # ========================================
    cur.execute("""
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
    """)
    
    # ========================================
    # TABLE: FILIERES
    # ========================================
    cur.execute("""
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
    """)
    
    # ========================================
    # TABLE: USERS
    # ========================================
    cur.execute("""
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
    """)
    
    # ========================================
    # TABLE: CHAT_SESSIONS
    # ========================================
    cur.execute("""
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT UNIQUE NOT NULL,
            user_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            metadata TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
        )
    """)
    
    # ========================================
    # TABLE: MESSAGES
    # ========================================
    cur.execute("""
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
    """)
    
    # ========================================
    # TABLE: PREINSCRIPTIONS
    # ========================================
    cur.execute("""
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
    """)
    
    # ========================================
    # INDEX pour améliorer les performances
    # ========================================
    cur.execute("CREATE INDEX IF NOT EXISTS idx_filieres_etablissement ON filieres(etablissement_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_preinscriptions_user ON preinscriptions(user_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_preinscriptions_etablissement ON preinscriptions(etablissement_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_preinscriptions_filiere ON preinscriptions(filiere_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_preinscriptions_statut ON preinscriptions(statut)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_chat_sessions_session_id ON chat_sessions(session_id)")
    
    # ========================================
    # DONNÉES DE TEST (Établissement et Filières)
    # ========================================
    
    # Vérifier si des données existent déjà
    cur.execute("SELECT COUNT(*) FROM etablissements")
    if cur.fetchone()[0] == 0:
        # Ajouter un établissement par défaut
        cur.execute("""
            INSERT INTO etablissements (nom, code, adresse, ville, telephone, email, site_web, type, actif)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            'ICT University',
            'ICTU',
            'Avenue de la République',
            'Yaoundé',
            '+237 6XX XXX XXX',
            'contact@ictuniversity.cm',
            'https://ictuniversity.cm',
            'université',
            1
        ))
        
        etablissement_id = cur.lastrowid
        
        # Ajouter des filières par défaut
        filieres_data = [
            # Licences
            ('Licence en Informatique Générale', 'L-INFO', 'Licence', 'Informatique', 3, 25000, 450000, 50, 
             'Formation complète en informatique générale avec spécialisations en développement web, mobile et desktop.',
             'BAC série C, D ou E avec moyenne minimale de 12/20', 1),
            
            ('Licence en Génie Logiciel', 'L-GL', 'Licence', 'Informatique', 3, 25000, 450000, 40,
             'Formation axée sur l\'architecture logicielle, le DevOps et les méthodologies Agile.',
             'BAC série C, D ou E avec moyenne minimale de 12/20', 1),
            
            ('Licence en Réseaux & Télécommunications', 'L-RT', 'Licence', 'Réseaux', 3, 25000, 450000, 35,
             'Spécialisation en administration réseaux, systèmes et télécommunications avec certifications CCNA.',
             'BAC série C, D ou E avec moyenne minimale de 12/20', 1),
            
            ('Licence en Cybersécurité', 'L-CYBER', 'Licence', 'Sécurité', 3, 25000, 450000, 30,
             'Formation en sécurité informatique, hacking éthique et gestion des systèmes sécurisés.',
             'BAC série C, D ou E avec moyenne minimale de 13/20', 1),
            
            # Masters
            ('Master en Intelligence Artificielle & Data Science', 'M-IA', 'Master', 'Informatique', 2, 35000, 650000, 25,
             'Spécialisation en Machine Learning, Deep Learning, NLP avec Python, TensorFlow et PyTorch.',
             'Licence en Informatique ou domaine connexe avec moyenne minimale de 13/20', 1),
            
            ('Master en Cloud Computing & DevOps', 'M-CLOUD', 'Master', 'Informatique', 2, 35000, 650000, 20,
             'Formation sur AWS, Azure, Google Cloud, Kubernetes, Docker et CI/CD.',
             'Licence en Informatique ou domaine connexe avec moyenne minimale de 13/20', 1),
            
            ('Master en Blockchain & Web3', 'M-BLOCK', 'Master', 'Informatique', 2, 35000, 650000, 15,
             'Technologies blockchain, Ethereum, Solidity, Smart Contracts, DApps, NFT et DeFi.',
             'Licence en Informatique ou domaine connexe avec moyenne minimale de 13/20', 1),
        ]
        
        for filiere in filieres_data:
            cur.execute("""
                INSERT INTO filieres (
                    etablissement_id, nom, code, niveau, departement, duree, 
                    frais_inscription, frais_scolarite, places_disponibles, 
                    description, prerequis, actif
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (etablissement_id,) + filiere)
        
        print(f"✅ Établissement 'ICT University' créé avec {len(filieres_data)} filières")
    
    conn.commit()
    conn.close()
    
    print(f"✅ Base de données initialisée avec succès: {DB_PATH}")
    print(f"📊 Tables créées: etablissements, filieres, users, chat_sessions, messages, preinscriptions")
    print(f"🔗 Relations et contraintes de clés étrangères activées")
    print(f"📈 Index créés pour optimiser les performances")

if __name__ == '__main__':
    init_db()
