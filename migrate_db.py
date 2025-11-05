"""
Script de migration de la base de données
Ajoute les nouvelles tables établissements et filières sans perdre les données existantes
"""

import sqlite3
import os

DB_PATH = "database/chatbot.db"

def migrate_database():
    """Migre la base de données vers la nouvelle structure"""
    
    if not os.path.exists(DB_PATH):
        print("❌ Base de données non trouvée. Exécutez d'abord init_db.py")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("🔄 Début de la migration...")
    
    try:
        # Active les contraintes de clés étrangères
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # Vérifier si la table établissements existe déjà
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='etablissements'")
        if not cursor.fetchone():
            print("📊 Création de la table etablissements...")
            cursor.execute("""
                CREATE TABLE etablissements (
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
            print("✅ Table etablissements créée")
        else:
            print("ℹ️ Table etablissements existe déjà")
        
        # Vérifier si la table filières existe déjà
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='filieres'")
        if not cursor.fetchone():
            print("📊 Création de la table filieres...")
            cursor.execute("""
                CREATE TABLE filieres (
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
            print("✅ Table filieres créée")
        else:
            print("ℹ️ Table filieres existe déjà")
        
        # Vérifier la structure de la table preinscriptions
        cursor.execute("PRAGMA table_info(preinscriptions)")
        columns = [col[1] for col in cursor.fetchall()]
        
        has_etablissement_id = 'etablissement_id' in columns
        has_filiere_id = 'filiere_id' in columns
        
        if not has_etablissement_id or not has_filiere_id:
            print("📊 Mise à jour de la table preinscriptions...")
            
            # Renommer l'ancienne table
            cursor.execute("ALTER TABLE preinscriptions RENAME TO preinscriptions_old")
            
            # Créer la nouvelle table
            cursor.execute("""
                CREATE TABLE preinscriptions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    etablissement_id INTEGER NOT NULL DEFAULT 1,
                    filiere_id INTEGER NOT NULL DEFAULT 1,
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
                    statut TEXT DEFAULT 'nouveau',
                    accept_terms INTEGER DEFAULT 0,
                    newsletter INTEGER DEFAULT 0,
                    date_soumission TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    meta_json TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
                    FOREIGN KEY (etablissement_id) REFERENCES etablissements(id) ON DELETE RESTRICT,
                    FOREIGN KEY (filiere_id) REFERENCES filieres(id) ON DELETE RESTRICT
                )
            """)
            
            # Copier les données (mapping des anciens champs vers les nouveaux)
            try:
                cursor.execute("""
                    INSERT INTO preinscriptions (
                        id, nom, prenom, email, telephone, date_naissance, lieu_naissance,
                        adresse, niveau, motivation, photo_path, diplome_path,
                        releve_path, cv_path, accept_terms, newsletter, 
                        date_soumission, meta_json, etablissement_id, filiere_id
                    )
                    SELECT 
                        id, nom, prenom, email, telephone, date_naissance, lieu_naissance,
                        adresse, niveau, motivation, photo_path, diplome_path,
                        releve_path, cv_path, accept_terms, newsletter,
                        date_soumission, meta_json, 1 as etablissement_id, 1 as filiere_id
                    FROM preinscriptions_old
                """)
                print(f"✅ {cursor.rowcount} préinscriptions migrées")
            except Exception as e:
                print(f"⚠️ Erreur lors de la migration des données: {e}")
            
            # Supprimer l'ancienne table
            cursor.execute("DROP TABLE IF EXISTS preinscriptions_old")
            print("✅ Table preinscriptions mise à jour")
        else:
            print("ℹ️ Table preinscriptions déjà à jour")
        
        # Insérer des données de test
        cursor.execute("SELECT COUNT(*) FROM etablissements")
        if cursor.fetchone()[0] == 0:
            print("📝 Insertion des données de test...")
            
            cursor.execute("""
                INSERT INTO etablissements (nom, code, adresse, ville, telephone, email, site_web, type, actif)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, ('ICT University', 'ICTU', 'Avenue de la République', 'Yaoundé',
                  '+237 6XX XXX XXX', 'contact@ictuniversity.cm', 'https://ictuniversity.cm', 'université', 1))
            
            etablissement_id = cursor.lastrowid
            
            # Filières
            filieres = [
                (etablissement_id, 'Licence en Informatique Générale', 'L-INFO', 'Licence', 'Informatique', 3, 25000, 450000, 50,
                 'Formation complète en informatique générale', 'BAC série C, D ou E', 1),
                (etablissement_id, 'Licence en Génie Logiciel', 'L-GL', 'Licence', 'Informatique', 3, 25000, 450000, 40,
                 'Architecture logicielle et DevOps', 'BAC série C, D ou E', 1),
                (etablissement_id, 'Licence en Réseaux & Télécommunications', 'L-RT', 'Licence', 'Réseaux', 3, 25000, 450000, 35,
                 'Administration réseaux et systèmes', 'BAC série C, D ou E', 1),
                (etablissement_id, 'Licence en Cybersécurité', 'L-CYBER', 'Licence', 'Sécurité', 3, 25000, 450000, 30,
                 'Sécurité informatique et hacking éthique', 'BAC série C, D ou E', 1),
                (etablissement_id, 'Master en Intelligence Artificielle', 'M-IA', 'Master', 'Informatique', 2, 35000, 650000, 25,
                 'IA, Machine Learning et Data Science', 'Licence en Informatique', 1),
                (etablissement_id, 'Master en Cloud Computing', 'M-CLOUD', 'Master', 'Informatique', 2, 35000, 650000, 20,
                 'AWS, Azure, Docker, Kubernetes', 'Licence en Informatique', 1),
                (etablissement_id, 'Master en Blockchain', 'M-BLOCK', 'Master', 'Informatique', 2, 35000, 650000, 15,
                 'Blockchain, Ethereum, Smart Contracts', 'Licence en Informatique', 1),
            ]
            
            for filiere in filieres:
                cursor.execute("""
                    INSERT INTO filieres (etablissement_id, nom, code, niveau, departement, duree,
                                         frais_inscription, frais_scolarite, places_disponibles,
                                         description, prerequis, actif)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, filiere)
            
            print(f"✅ {len(filieres)} filières insérées")
        
        # Vérifier et ajouter la colonne password_hash à la table users
        print("🔐 Vérification de la table users...")
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'password_hash' not in columns:
            print("📝 Ajout de la colonne password_hash...")
            cursor.execute("ALTER TABLE users ADD COLUMN password_hash TEXT")
            print("✅ Colonne password_hash ajoutée")
        else:
            print("ℹ️ Colonne password_hash existe déjà")
        
        # Vérifier la colonne role
        if 'role' not in columns:
            print("📝 Ajout de la colonne role...")
            cursor.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'etudiant'")
            print("✅ Colonne role ajoutée")
        else:
            print("ℹ️ Colonne role existe déjà")
        
        # Vérifier la colonne created_at
        if 'created_at' not in columns:
            print("📝 Ajout de la colonne created_at...")
            cursor.execute("ALTER TABLE users ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
            print("✅ Colonne created_at ajoutée")
        else:
            print("ℹ️ Colonne created_at existe déjà")
        
        # Créer les index
        print("📈 Création des index...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_filieres_etablissement ON filieres(etablissement_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_preinscriptions_user ON preinscriptions(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_preinscriptions_etablissement ON preinscriptions(etablissement_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_preinscriptions_filiere ON preinscriptions(filiere_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_preinscriptions_statut ON preinscriptions(statut)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id)")
        print("✅ Index créés")
        
        # Afficher la structure finale de la table users
        print("\n📊 Structure finale de la table users:")
        cursor.execute("PRAGMA table_info(users)")
        for column in cursor.fetchall():
            print(f"  - {column[1]}: {column[2]} {'NOT NULL' if column[3] else ''}")
        
        conn.commit()
        print("\n✅ Migration terminée avec succès!")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Erreur lors de la migration: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == '__main__':
    migrate_database()
