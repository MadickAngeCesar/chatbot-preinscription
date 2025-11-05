"""
Script pour créer un utilisateur de test avec mot de passe haché
"""
import sqlite3
import hashlib
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, "database")
DB_PATH = os.path.join(DB_DIR, "chatbot.db")

def hash_password(password):
    """Hache un mot de passe avec SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_test_user():
    """Crée un utilisateur de test"""
    
    if not os.path.exists(DB_PATH):
        print("❌ Base de données introuvable. Exécutez d'abord init_db.py")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Utilisateur de test
        test_users = [
            {
                'nom': 'Test',
                'prenom': 'User',
                'email': 'test@example.com',
                'telephone': '+221 77 123 4567',
                'password': 'TestPass123',
                'role': 'etudiant'
            },
            {
                'nom': 'Admin',
                'prenom': 'Super',
                'email': 'admin@ict.sn',
                'telephone': '+221 77 000 0000',
                'password': 'AdminPass123',
                'role': 'admin'
            }
        ]
        
        for user in test_users:
            # Vérifier si l'utilisateur existe déjà
            cursor.execute("SELECT id FROM users WHERE email = ?", (user['email'],))
            existing = cursor.fetchone()
            
            if existing:
                print(f"ℹ️ Utilisateur {user['email']} existe déjà (ID: {existing[0]})")
                # Mettre à jour le mot de passe
                password_hash = hash_password(user['password'])
                cursor.execute("""
                    UPDATE users 
                    SET password_hash = ?, nom = ?, prenom = ?, telephone = ?, role = ?
                    WHERE email = ?
                """, (password_hash, user['nom'], user['prenom'], user['telephone'], user['role'], user['email']))
                print(f"✅ Mot de passe mis à jour pour {user['email']}")
            else:
                # Créer le nouvel utilisateur
                password_hash = hash_password(user['password'])
                cursor.execute("""
                    INSERT INTO users (nom, prenom, email, telephone, password_hash, role)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (user['nom'], user['prenom'], user['email'], user['telephone'], password_hash, user['role']))
                user_id = cursor.lastrowid
                print(f"✅ Utilisateur créé: {user['email']} (ID: {user_id})")
            
            print(f"   📧 Email: {user['email']}")
            print(f"   🔑 Mot de passe: {user['password']}")
            print(f"   👤 Rôle: {user['role']}")
            print()
        
        conn.commit()
        
        # Afficher tous les utilisateurs
        print("📊 Liste des utilisateurs:")
        cursor.execute("SELECT id, nom, prenom, email, role, created_at FROM users")
        users = cursor.fetchall()
        
        for user in users:
            print(f"  [{user[0]}] {user[2]} {user[1]} - {user[3]} ({user[4]})")
        
        print(f"\n👥 Total: {len(users)} utilisateur(s)")
        
    except sqlite3.Error as e:
        print(f"❌ Erreur: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    print("👤 Création des utilisateurs de test...\n")
    create_test_user()
    print("\n✅ Terminé !")
